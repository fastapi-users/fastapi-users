# 2.x.x ➡️ 3.x.x

## Emails are now case-insensitive

Before 3.x.x, the local part (before the @) of the email address was case-sensitive. Therefore, `king.arthur@camelot.bt` and `King.Arthur@camelot.bt` were considered as **two different users**. This behaviour was a bit confusing and not consistent with 99% of web services out there.

After 3.x.x, users are fetched from the database with a case-insensitive email search. Bear in mind though that if the user registers with the email `King.Arthur@camelot.bt`, it will be stored exactly like this in the database (with casing) ; but he will be able to login as `king.arthur@camelot.bt`.

!!! danger
    It's super important then, before you upgrade to 3.x.x that you **check if there are several users with the same email with different cases** ; and that you **merge or delete those accounts**.
