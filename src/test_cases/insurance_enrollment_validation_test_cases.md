# Insurance Enrollment File Data Validation Test Cases

**Industry:** Insurance  
**Use Case:** Enrollment File Data Validation  
**Dataset Type:** Synthetic Evaluation Dataset

---

## Test Case EV-001: Mandatory Field Validation
**Question:** An enrollment ADD record contains member ID MBR-10001, plan code DEN-PPO-01, and coverage effective date 2026-01-01, but the subscriber's last name is blank. Should the record pass validation?

**Expected Answer:** No. Disqualify the record because a required member name field is missing. Return an error identifying the missing subscriber last name and route the record for correction before enrollment processing.

---

## Test Case EV-002: Date Validation
**Question:** An enrollment record has coverage effective date 2026-03-01 and coverage termination date 2026-02-28. Is the date sequence valid?

**Expected Answer:** No. The termination date occurs before the effective date. Reject the coverage segment and report an invalid coverage date sequence.

---

## Test Case EV-003: Duplicate Enrollment
**Question:** The file contains two ADD transactions for member MBR-10003 with the same group ID GRP-200, plan code VIS-BASIC-01, and effective date 2026-01-01. How should they be handled?

**Expected Answer:** Treat the transactions as potential duplicates. Do not load both records. Retain one valid transaction or route both for review according to the configured duplicate-resolution policy, and report the duplicate business key.

---

## Test Case EV-004: Plan Code Validation
**Question:** A member enrollment references plan code MED-GOLD-99, but that code is absent from the approved plan master for group GRP-201. Should the enrollment be accepted?

**Expected Answer:** No. Reject or hold the record because the plan code is not valid for the group. Return an error stating that MED-GOLD-99 is not mapped to an approved plan for GRP-201.

---

## Test Case EV-005: Dependent Relationship Validation
**Question:** A dependent record identifies relationship type Spouse but does not reference a subscriber member ID. Can the dependent be enrolled?

**Expected Answer:** No. A dependent must be linked to a valid subscriber. Reject or pend the dependent record and report the missing subscriber relationship reference.

---

## Test Case EV-006: Maintenance Action Validation
**Question:** A TERMINATE transaction is received for member MBR-10006, but no active coverage exists for the specified group and plan. What is the expected result?

**Expected Answer:** Do not apply the termination automatically. Mark the transaction as unmatched and route it for reconciliation because there is no active enrollment to terminate.

---

## Test Case EV-007: Format Validation
**Question:** The date-of-birth field contains 1985-13-40. Is the value valid, and what should the validator return?

**Expected Answer:** No. The value is not a valid calendar date. Reject the record and return a date format or invalid date error for the date-of-birth field.

---

## Test Case EV-008: Coverage Overlap
**Question:** Member MBR-10008 already has active dental coverage from 2026-01-01 through 2026-12-31. A second enrollment for the same dental benefit is submitted with dates 2026-06-01 through 2027-05-31. What should happen?

**Expected Answer:** Flag the record for overlapping coverage. Do not create concurrent coverage for the same member and benefit unless the group rules explicitly permit it. Route the record for correction or coordinated replacement processing.

---

## Test Case EV-009: Control Total Validation
**Question:** The enrollment file trailer reports 250 member records, but only 249 member records are present in the file. Should the file proceed?

**Expected Answer:** No. Reject or quarantine the file because the reported control total does not match the actual member-record count. Return a file-level balancing error.

---

## Test Case EV-010: Cross-Field Consistency
**Question:** A record has maintenance action ADD, employment status Terminated, and a future coverage effective date, with no continuation or exception indicator. Is the record internally consistent?

**Expected Answer:** No. The fields conflict. Pend or reject the enrollment and report that an ADD action with terminated employment requires a valid continuation or configured exception before coverage can begin.
