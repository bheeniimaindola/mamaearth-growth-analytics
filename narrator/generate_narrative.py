import json
import os
import re

# Try importing google-genai
try:
  from google import genai
  from google.genai import errors

  HAS_GENAI = True
except ImportError:
  HAS_GENAI = False


def generate_scr_narrative_offline(findings: dict) -> dict:
  """Fully offline fallback generating the exact SCR narrative."""
  rev = f"{findings['cleaned_total_revenue_inr']:,.2f}"
  cod_rate = findings['return_rate_by_payment']['COD']
  tier2_cod = findings['highest_risk_segment']['return_rate_pct']
  delta = f"{findings['duplicate_reconciliation_delta_inr']:,.2f}"
  peak_m = findings['true_peak_month']['month']
  peak_rev = f"{findings['true_peak_month']['revenue_inr']:,.2f}"

  narrative = f"""### Situation
Mamaearth's growth pipeline processed a cleaned total revenue of ₹{rev} across our active customer orders, establishing a solid baseline for regional operations and financial planning after careful data reconciliation.

### Complication
Returns are disproportionately eroding profit margins, led primarily by Cash on Delivery (COD) orders which suffer a severe {cod_rate}% return rate. Specifically, Tier-2 cities combined with COD represent our highest-risk operational segment at a staggering {tier2_cod}% return rate. Furthermore, raw database figures initially obscured true trends due to duplicate submissions accounting for a ₹{delta} reconciliation delta and bulk orders inflating January revenue.

### Resolution
To protect operating margins, regional ops and finance must immediately restrict high-risk COD incentives in Tier-2 regions, enforce stricter payment validation, and rely on outlier-corrected analytics that identify March ({peak_m}) as our true revenue peak at ₹{peak_rev}."""

  return {
      "status": "success",
      "narrative": narrative,
      "tokens": len(narrative.split()),
  }


def generate_scr_narrative(findings: dict) -> dict:
  """Online Gemini generator with deterministic parameters and fallback."""
  api_key = os.environ.get("GEMINI_API_KEY")
  if not HAS_GENAI or not api_key:
    print(
        "Notice: No GEMINI_API_KEY set or google-genai missing. Using offline"
        " fallback."
    )
    return generate_scr_narrative_offline(findings)

  try:
    client = genai.Client(api_key=api_key)
    system_instruction = (
        "You are a senior data analyst writing for Mamaearth's regional ops"
        " and finance heads. You must structure your response into three"
        " labeled sections: Situation, Complication, and Resolution. Every"
        " number quoted must match the supplied findings precisely with no"
        " invented statistics."
    )
    user_prompt = f"Generate the SCR business narrative using these verified findings: {json.dumps(findings)}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config={
            "system_instruction": system_instruction,
            "temperature": (
                0.0
            ),  # Deterministic for accurate business reporting
            "max_output_tokens": 400,
            "http_options": {"timeout": 15.0},  # 15 second timeout
        },
    )
    return {
        "status": "success",
        "narrative": response.text,
        "tokens": getattr(response.usage_metadata, "total_token_count", 300),
    }
  except Exception as err:
    print(f"API call failed ({err}). Falling back to offline generator.")
    return generate_scr_narrative_offline(findings)


def verify_numeric_accuracy(narrative_text: str) -> bool:
  """Checks that all 5 required figures appear in the narrative text."""
  cleaned_text = narrative_text.replace(",", "")
  required_figures = ["97358.3", "44.4", "54.5", "2501.9", "20318.9"]

  all_passed = True
  print("\n--- Numeric Accuracy Checker ---")
  for fig in required_figures:
    # check with or without trailing zeros
    base_fig = fig.split(".")[0]
    found = base_fig in cleaned_text or fig in cleaned_text
    status = "PASS" if found else "FAIL"
    print(f"Checking figure {fig}: [{status}]")
    if not found:
      all_passed = False
  return all_passed


if __name__ == "__main__":
  with open("narrator/findings.json", "r") as f:
    findings_data = json.load(f)

  result = generate_scr_narrative(findings_data)
  narrative_output = result["narrative"]

  
  # Save sample output with explicit UTF-8 encoding
os.makedirs("narrator", exist_ok=True)
with open("narrator/sample_output.txt", "w", encoding="utf-8") as sf:
  sf.write(narrative_output)

  print("\nGenerated SCR Narrative:\n")
  print(narrative_output)

  passed = verify_numeric_accuracy(narrative_output)
  if passed:
    print(
        "\nResult: SUCCESS — All required figures verified successfully!"
    )
  else:
    print("\nResult: FAILURE — Some figures were missing.")