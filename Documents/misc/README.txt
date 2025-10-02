Changes with this commit
-ben_type_id matched with ben_type_desc
-service_type matched with IN or OUT PATIENT
-Minimum limit on allocation to 10,000
-Error and exception handling on publish benefit when service is unavailable
-Matching cln_ben_code to match cln_ben_clause_code

TODO To add child parent scenario below. For now, no c/p implemented hence a hyphen as default
Normal	TODO We have a BOTH case at Minet. How do we handle that on Smart side
Normal	TODO To clarify below on the cln_ben_code and cln_ben_clause_code relationship

10-Oct-2018
- Change from parametrical update for claim approvals to direct update due to update not being effected. Old code is commented below the working code
- Error with the Message box when no claims fixed.

