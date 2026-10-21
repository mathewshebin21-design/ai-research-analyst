# Legal launch checklist (UK)

These documents are careful drafts written for a UK limited company selling a business-to-business research tool. **They are not legal advice.** Have a UK solicitor review them before you take payment or onboard customers who upload personal data. Fixed-fee startup legal reviews are widely available.

## Before inviting anyone outside your team

- [ ] Fill in every placeholder in `legal/company.json` (company name, number, address, emails, ICO number). The web app shows a warning banner on legal pages until they are filled.
- [ ] Decide the trading entity. The terms assume a limited company; a sole trader needs wording changes.
- [ ] Pay the ICO data protection fee and add the registration number (check the current tier and amount at ico.org.uk/fee).
- [ ] Choose EU or UK regions for Supabase, the API host and Sentry, and update `legal/subprocessors.md`.
- [ ] Confirm you are on the **paid** tier of the Gemini API. On Google's unpaid tier, content may be used to improve Google's products, which would make the AI notice and privacy notice wrong.
- [ ] Check Tavily's and Google's current terms allow your commercial use and resale of outputs.
- [ ] Write a short record of processing activities (ROPA) and a data protection impact assessment screening. The ICO publishes templates for both.
- [ ] Set backup retention to 35 days or less in your database provider, and log retention to 30 days on your hosts, to match the privacy notice.
- [ ] Set up the privacy and contact mailboxes and a process to answer requests within one month.
- [ ] Consider professional indemnity and cyber insurance, since customers may make decisions using outputs.

## When you add payments

- [ ] Add pricing, billing period, renewal and cancellation terms to section 8 of the terms.
- [ ] If any customers could be consumers, add Consumer Contracts Regulations information and the 14-day cancellation right, or restrict sign-up to businesses (the terms currently state the Service is for business use).
- [ ] Register for VAT once taxable turnover passes the threshold (check gov.uk for the current figure), and handle VAT on digital services sold to EU customers.
- [ ] Add Stripe to the subprocessor list and privacy notice.

## Each time something changes

- [ ] Changing a legal document: bump `version` in `company.json` and `TERMS_VERSION` / `PRIVACY_VERSION` in the API settings. Users are then asked to accept again, and the acceptance is recorded.
- [ ] Adding a provider that sees customer content: update the subprocessor page at least 14 days before (DPA section 2.4).
