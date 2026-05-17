# Wiki operations log

Append-only chronological log. Every batch of wiki edits ends with an entry here
summarizing what changed and why.

Format:
```
## YYYY-MM-DD — <one-line summary>
- created: [[category/slug]] — <reason>
- updated: [[category/slug]] — <reason>
- deleted: <none expected; wiki is append-mostly>
```

---
