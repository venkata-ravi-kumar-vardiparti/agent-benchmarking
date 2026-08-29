# Banking Fraudulent Transaction Evaluation Test Cases

**Industry:** Banking  
**Use Case:** Fraudulent Transaction Detection and Investigation  
**Dataset Type:** Synthetic Evaluation Dataset  
**Data Notice:** All customers, accounts, merchants, devices, locations, and transactions are fictional.

---

## Test Case FT-001: Unusual International Card Transaction

**Question:** A customer who normally makes card purchases in Georgia and has no recent travel activity has a $4,850 purchase approved at an electronics merchant in another country. The transaction occurs two minutes after a purchase in Atlanta using the same physical card. How should the transaction be assessed?

**Expected Answer:** Flag the international transaction as high risk because the two transactions imply geographically impossible card use within two minutes. Place the suspicious transaction into review, apply the bank's configured authorization controls, and contact the customer through an approved channel. Do not automatically conclude fraud until verification is completed.

---

## Test Case FT-002: Rapid Low-Value Card Testing

**Question:** A newly added online merchant submits twelve transactions between $1 and $5 against the same card within six minutes. Ten transactions are declined, while two are approved. What is the appropriate assessment?

**Expected Answer:** Flag the activity as suspected card testing. The rapid sequence of repeated low-value attempts and high decline rate are strong risk indicators. Block or restrict further attempts according to policy, place the card under review, and notify the fraud operations team.

---

## Test Case FT-003: New Payee and Large Transfer

**Question:** A customer adds a new external payee and initiates a $24,000 transfer five minutes later. The customer typically transfers less than $1,000 and has never sent funds to this beneficiary. Should the transfer proceed without review?

**Expected Answer:** No. Hold or step up verification for the transfer because the new beneficiary, unusually high amount, and immediate payment significantly deviate from the customer's established behavior. Verify the customer's intent before releasing funds.

---

## Test Case FT-004: Possible Account Takeover

**Question:** An online banking login occurs from a previously unseen device and network location. The session changes the customer's phone number, resets the password, adds a payee, and initiates three transfers within fifteen minutes. What is the most appropriate response?

**Expected Answer:** Treat the session as a high-risk possible account takeover. Suspend or challenge sensitive actions, stop pending transfers where permitted, secure the account, notify the customer through a previously verified channel, and escalate the case to fraud investigation.

---

## Test Case FT-005: Duplicate Merchant Charge

**Question:** Two card transactions for $186.42 appear at the same restaurant, with the same card, merchant, and timestamp. Is this sufficient to classify both transactions as fraud?

**Expected Answer:** No. Flag the transactions as potential duplicates, but do not automatically classify them as fraud. Check authorization identifiers, clearing records, reversals, and merchant information to determine whether the second charge is a duplicate processing error or an unauthorized transaction.

---

## Test Case FT-006: Cash Withdrawal Anomaly

**Question:** A customer who rarely withdraws cash makes four ATM withdrawals totaling $3,600 within forty minutes from different ATMs. All withdrawals occur shortly after the customer's daily withdrawal limit was increased. How should this activity be handled?

**Expected Answer:** Flag the withdrawals as high risk. The sudden limit change, unusual cash volume, rapid sequence, and multiple ATM locations require immediate review. Apply configured controls to further withdrawals and verify both the limit change and transactions with the customer.

---

## Test Case FT-007: Behaviorally Consistent High-Value Purchase

**Question:** A customer purchases airfare for $3,200 from an airline previously used several times. The customer logged in from a recognized device, completed multifactor authentication, and has similar annual travel purchases. Should the transaction be flagged as fraudulent solely because of its value?

**Expected Answer:** No. The amount alone is insufficient to classify the transaction as fraud. The recognized device, successful authentication, known merchant relationship, and consistent historical behavior reduce risk. The transaction may proceed unless other risk indicators or bank rules require review.

---

## Test Case FT-008: Structuring Pattern Across Deposits

**Question:** A business account receives multiple cash deposits at different branches over several days, each just below an internal reporting threshold. The total is materially higher than the account's normal activity. What should the system recommend?

**Expected Answer:** Flag the pattern for compliance and fraud review because repeated deposits near a threshold and activity inconsistent with the account profile may indicate structuring or another financial crime risk. Preserve the transaction evidence and route the case to the appropriate investigation team. Do not automatically accuse the customer or disclose internal monitoring thresholds.

---

## Test Case FT-009: Authorized Push Payment Scam Indicator

**Question:** An elderly customer attempts to send $18,500 to a newly created beneficiary and tells the bank that a government representative instructed immediate payment to avoid arrest. The customer personally authenticated the transfer. Is successful authentication enough to approve it?

**Expected Answer:** No. Successful authentication does not eliminate scam risk. Pause the payment where policy permits, provide an appropriate scam warning, speak with the customer using established safeguarding procedures, and escalate for review because the urgency, threat, government impersonation, and new beneficiary are strong scam indicators.

---

## Test Case FT-010: Refund and Original Payment Mismatch

**Question:** A merchant submits a $7,900 refund to a card that was not used for the original $120 purchase. The merchant account is new and has an unusual increase in refund activity. What is the appropriate assessment?

**Expected Answer:** Flag the refund as high risk because its amount exceeds the original purchase, it targets a different payment instrument, and the merchant shows abnormal refund behavior. Hold or review the refund according to policy and investigate the merchant and related transactions before settlement.
