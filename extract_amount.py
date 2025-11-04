import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime
try:
    from dateutil import parser as _dateutil_parser
except Exception:
    _dateutil_parser = None

load_dotenv()

_genai_model = None
def _get_genai_model():
    global _genai_model
    if _genai_model is not None:
        return _genai_model
    api_key = os.getenv("gemini_api_key")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    _genai_model = genai.GenerativeModel("models/gemini-2.5-flash")
    return _genai_model


def extract_amount_and_date(text: str):
    # preprocessing helpers to make ocr output cleaner for the llm
    def _clean_text(s: str) -> str:
        s = re.sub(r"[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]+", "", s)
        s = s.replace('\r\n', '\n').replace('\r', '\n')
        s = re.sub(r"\n{2,}", "\n", s)
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in s.split('\n')]
        return "\n".join([ln for ln in lines if ln])

    def _normalize_common_ocr_errors(s: str) -> str:
        #fixing common ocr confusions in numeric contexts
        #replace letter O with zero when surrounded by digits
        s = re.sub(r"(?<=\d)O(?=\d)", "0", s)
        s = re.sub(r"(?<=\d)l(?=\d)", "1", s)
        s = re.sub(r"(?<=\d)S(?=\d)", "5", s)
        return s


    def _candidate_lines(s: str):
        #returns lines that likely contain amounts or dates or keywords
        lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
        keywords = ["total", "amount", "balance", "subtotal", "grand", "bill", "net", "due"]
        cand = []
        for i, ln in enumerate(lines):
            lower = ln.lower()
            # include lines with money like patterns or keywords
            if any(k in lower for k in keywords) or re.search(r"\d[\d,]*[\.]?\d{0,2}", ln):
                cand.append((i, ln))
        # include few surrounding lines for context
        indexes = set()
        for i, _ in cand:
            for j in range(max(0, i - 2), i + 3):
                indexes.add(j)
        result = [lines[i] for i in sorted(indexes) if 0 <= i < len(lines)]
        return result


    # detect likely phone numbers or addresses to avoid picking them as totals
    def _looks_like_phone_or_address(s: str) -> bool:
        low = s.lower()
        # phone patterns
        if re.search(r"\b(?:\+\d{1,3}[ -]?)?(?:\d{2,4}[ -]?){2,}\d{2,4}\b", s):
            return True
        # common address keywords
        if any(w in low for w in ["street", "st", "road", "rd", "drive", "dr", "lane", "ln", "avenue", "ave", "suite", "ste", "floor", "unit", "block", "p.o.", "postal", "pin", "zip", "tin", "gstin"]):
            return True
        return False


    # date parsing : tryin regexes and dateutil 
    def _parse_date_from_line(line: str):
        # common date regexes
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
            r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4})",
            r"([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})",
        ]
        for p in patterns:
            m = re.search(p, line)
            if m:
                ds = m.group(1)
                # dateutil for parsing
                if _dateutil_parser:
                    try:
                        return _dateutil_parser.parse(ds, dayfirst=False).strftime("%Y-%m-%d")
                    except Exception:
                        pass
                # fallback to manual formats
                for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"):
                    try:
                        return datetime.strptime(ds, fmt).strftime("%Y-%m-%d")
                    except Exception:
                        continue
        return None

    cleaned = _clean_text(text)
    cleaned = _normalize_common_ocr_errors(cleaned)

    # quick line-based regex , first attempt for date and total (fast, often works)
    total_amount = None
    extracted_date = None
    lines = cleaned.split('\n')
    # prefer explicit grand/total/amount due labels in lines (avoid matching address numbers)
    for ln in lines:
        lower = ln.lower()
        # date detection per line
        date_m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", ln)
        if date_m and not extracted_date:
            date_str = date_m.group(1)
            for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y"):
                try:
                    extracted_date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    break
                except Exception:
                    continue

    # Helper , find a numeric amount occurring after a keyword in the same line
    def _amount_after_keyword(line: str, keyword: str):
        lower = line.lower()
        pos = lower.find(keyword)
        # if keyword not found try whole line
        search_zone = line[pos:] if pos >= 0 else line
        m = re.search(r"([\d][\d,]*\.?\d{0,2})", search_zone)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except Exception:
                return None
        return None

    # find explicit grand total or amount due first (prefering numbers that appear after the keyword)
    for ln in lines:
        lower = ln.lower()
        if 'grand total' in lower:
            amt = _amount_after_keyword(ln, 'grand total')
            if amt is not None:
                total_amount = amt
                break
        if 'amount due' in lower or 'amount due:' in lower:
            amt = _amount_after_keyword(ln, 'amount due')
            if amt is not None:
                total_amount = amt
                break
        # plain 'total' but avoiding matching 'subtotal' lines
        if re.search(r"\btotal\b", lower) and 'sub' not in lower:
            amt = _amount_after_keyword(ln, 'total')
            if amt is not None:
                total_amount = amt
                break

    # if still not found , looking for subtotal line to compute fallback later (we keep subtotal captured)
    subtotal = None
    for ln in lines:
        lower = ln.lower()
        if 'sub total' in lower or 'subtotal' in lower:
            m = re.search(r"([\d][\d,]*\.?\d{0,2})", ln)
            if m:
                try:
                    subtotal = float(m.group(1).replace(',', ''))
                except Exception:
                    subtotal = None
                break

    # if quick regex found both , returning immediately
    if total_amount is not None and extracted_date is not None:
        return {"total_amount": total_amount, "date": extracted_date}

    # candidate lines early (used for labeled parsing and llm prompt)
    candidates = _candidate_lines(cleaned)

    # building scored candidates : each candidate line is scored and numeric tokens extracted
    def _find_numbers(line: str):
        return [(m.start(), m.group(1)) for m in re.finditer(r"([\d][\d,]*\.?\d{0,2})", line)]

    def _amount_near_label(line: str, label_patterns):
        lower = line.lower()
        nums = _find_numbers(line)
        if not nums:
            return None
        # find label position (last occurrence) among alternatives
        pos = -1
        for patt in label_patterns:
            p = lower.rfind(patt)
            if p > pos:
                pos = p
        # if label found, look for first number after label
        if pos >= 0:
            for start, num in nums:
                if start >= pos:
                    try:
                        return float(num.replace(',', ''))
                    except Exception:
                        continue
        # otherwise, as a fallback prefer the last numeric token if it looks like a currency (has a decimal)
        for start, num in reversed(nums):
            if '.' in num:
                try:
                    return float(num.replace(',', ''))
                except Exception:
                    continue
        # final fallback: return last number
        try:
            return float(nums[-1][1].replace(',', ''))
        except Exception:
            return None

    def _score_and_extract(candidates_list):
        scored = []
        total_lines = len(lines)
        for idx, ln in enumerate(candidates_list):
            low = ln.lower()
            if not ln.strip():
                continue
            # skip lines that look like addresses or phones
            is_address_like = _looks_like_phone_or_address(ln)
            # features
            score = 0
            if any(k in low for k in ["grand total", "amount due", "amount paid"]):
                score += 30
            if re.search(r"\btotal\b", low) and 'sub' not in low:
                score += 10
            if 'subtotal' in low or 'sub total' in low:
                score += 6
            if 'tip' in low:
                score += 6
            if 'service' in low:
                score += 4
            if re.search(r"[$₹£€]", ln):
                score += 8
            # prefer numbers with decimals 
            if re.search(r"\d+\.\d{1,2}", ln):
                score += 5
            # prefer lines appearing near the bottom of the receipt (heuristic)
            if idx >= max(0, len(candidates_list) - 5):
                score += 2
            # negativing address/phone like lines
            if is_address_like:
                score -= 20
            # extract numeric tokens and choose appropriate token
            amt = _amount_near_label(ln, ['total', 'grand total', 'amount due', 'subtotal', 'sub total', 'tip'])
            if amt is None:
                continue
            scored.append((score, ln, amt))
        # sort by score desc 
        scored.sort(key=lambda x: (x[0], x[2]), reverse=True)
        return scored

    scored_candidates = _score_and_extract(candidates)

    #parsing labeled amounts from candidate lines to prefer explicit Grand/Total labels.
    labeled = {}
    # examining candidate lines (including a few extra lines) for labeled amounts
    for ln in (candidates + [cleaned]):
        lower = ln.lower()
        # grand total
        if 'grand total' in lower:
            amt = _amount_near_label(ln, ['grand total'])
            if amt is not None:
                labeled['grand_total'] = amt
        # amount due/paid
        if re.search(r'\b(total\s*due|amount\s*due|amount\s*paid|amount\s*due)\b', lower):
            amt = _amount_near_label(ln, ['amount due', 'amount paid', 'total due'])
            if amt is not None:
                labeled['amount_due'] = amt

        if 'sub total' in lower or 'subtotal' in lower:
            amt = _amount_near_label(ln, ['sub total', 'subtotal'])
            if amt is not None:
                labeled['subtotal'] = amt
        
        if 'tip' in lower:
            amt = _amount_near_label(ln, ['tip'])
            if amt is not None:
                labeled['tip'] = amt
        
        if 'service' in lower or 'service charge' in lower:
            amt = _amount_near_label(ln, ['service charge', 'service'])
            if amt is not None:
                labeled.setdefault('service', amt)
        # taxes
        if re.search(r'cgst|sgst|tax', lower):
            amt = _amount_near_label(ln, ['cgst', 'sgst', 'tax'])
            if amt is not None:
                labeled.setdefault('taxes', 0.0)
                labeled['taxes'] += amt
        # generic 'total' (avoiding 'total qty' / 'total qly' etc.)
        if re.search(r'\btotal\b', lower) and 'sub' not in lower and not re.search(r'qty|qly|items|no\.|count', lower):
            amt = _amount_near_label(ln, ['total'])
            if amt is not None:
                labeled.setdefault('total', amt)


    # decide which labeled amount to use 
    if os.getenv('EXTRACT_DEBUG'):
        print('DEBUG labeled:', labeled)
    if 'grand_total' in labeled:
        total_amount = labeled['grand_total']
    elif 'amount_due' in labeled:
        total_amount = labeled['amount_due']
    else:
        # if subtotal + additions (tip/service/taxes) exist, prefer computed grand total
        if 'subtotal' in labeled:
            subtotal_val = labeled.get('subtotal', 0.0)
            tip = labeled.get('tip', 0.0)
            service = labeled.get('service', 0.0)
            taxes = labeled.get('taxes', 0.0)
            computed = subtotal_val + tip + service + taxes
            if computed > 0 and (tip or service or taxes):
                total_amount = computed
        # otherwise prefer an explicit 'total' label (if not already set)
        if total_amount is None and 'total' in labeled:
            total_amount = labeled['total']
        # as a last resort, if only subtotal exists use it
        if total_amount is None and 'subtotal' in labeled:
            total_amount = labeled.get('subtotal')

    #focused prompt using candidate lines to improve llm accuracy
    candidates = _candidate_lines(cleaned)
    prompt_context = "\n".join(candidates[:40])
    if not prompt_context:
        # fall back to the whole cleaned text but truncated
        prompt_context = cleaned[:4000]

    base_instruction = (
        "You are a financial assistant. Extract two fields from the provided receipt text:"
        " total_amount (a number) and date (YYYY-MM-DD or null)."
        " Return ONLY a single valid JSON object with these keys. If total_amount cannot be found, return -1. If date cannot be found, return null."
    )

    model = _get_genai_model()
    if model is not None:
        few_shot = (
            "Example 1:\n"
            "OCR text:\nStore ABC\nTotal: 1,234.56\nDate: 12/10/25\n\n"
            "JSON:\n{\"total_amount\": 1234.56, \"date\": \"2025-10-12\"}\n\n"
            "Example 2:\n"
            "OCR text:\nCorner Shop\nSub Total 100.00\nTip: 20.00\nService: 5.00\nGrand Total: 125.00\nDate: 2024-05-01\n\n"
            "JSON:\n{\"total_amount\": 125.0, \"date\": \"2024-05-01\"}\n\n"
        )

        full_prompt = (
            base_instruction
            + "\n\n" + few_shot
            + "Receipt lines to examine:\n"
            + prompt_context
            + "\n\nIMPORTANT: Return ONLY a single valid JSON object and NOTHING else."
        )

        def _call_model(prompt_text: str):
            try:
                resp = model.generate_content(prompt_text, temperature=0)
                out = resp.candidates[0].content.parts[0].text.strip()
                return out
            except Exception as e:
                if os.getenv('EXTRACT_DEBUG'):
                    print("LLM error:", e)
                return None

        raw_output = _call_model(full_prompt)

        # parse json , retry once with a stricter redirect if malformed
        data = None
        for attempt in range(2):
            if not raw_output:
                break
            m = re.search(r"(\{.*\})", raw_output, re.DOTALL)
            if m:
                json_str = m.group(1)
                try:
                    parsed = json.loads(json_str)
                    ta = parsed.get("total_amount", None)
                    dt = parsed.get("date", None)
                    try:
                        if ta is not None and ta != -1:
                            ta = float(str(ta).replace(',', ''))
                    except Exception:
                        ta = None
                    if dt:
                        try:
                            if _dateutil_parser:
                                dt = _dateutil_parser.parse(dt, dayfirst=False).strftime("%Y-%m-%d")
                            else:
                                for fmt in ("%Y-%m-%d", "%d/%m/%y", "%d/%m/%Y", "%m/%d/%y", "%m/%d/%Y"):
                                    try:
                                        dt = datetime.strptime(dt, fmt).strftime("%Y-%m-%d")
                                        break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                    data = {"total_amount": ta if ta is not None else parsed.get("total_amount", -1), "date": dt}
                    break
                except Exception:
                    raw_output = _call_model(full_prompt + "\n\nRETURN ONLY A VALID JSON OBJECT: {\"total_amount\": number, \"date\": \"YYYY-MM-DD\"|null}")
                    continue
            else:
                raw_output = _call_model(full_prompt + "\n\nRETURN ONLY A VALID JSON OBJECT: {\"total_amount\": number, \"date\": \"YYYY-MM-DD\"|null}")
                continue

        if data:
            ta_val = data.get("total_amount", -1)
            if ta_val not in [None, -1]:
                try:
                    total_amount = float(ta_val)
                    method_used = 'llm'
                    confidence = max(confidence, 0.95)
                except Exception:
                    pass
            if data.get("date"):
                extracted_date = data.get("date")
        else:
            if os.getenv('EXTRACT_DEBUG'):
                print("LLM did not return valid JSON; falling back to heuristics")
    else:
        if os.getenv('EXTRACT_DEBUG'):
            print("Gemini API key not configured; skipping LLM extraction")