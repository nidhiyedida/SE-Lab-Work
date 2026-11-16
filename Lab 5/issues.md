# Static Code Analysis — Issues

| Issue                         | Type              | Line(s) | Description                                                                            | Fix Approach                                                  |
|-------------------------------|-------------------|---------|----------------------------------------------------------------------------------------|-------------------------------------------------------|
| Weak MD5 hash                 | Security (High)   | 49      | MD5 is a weak hash algorithm and should not be used for security-sensitive purposes.   | Use SHA-256 if a cryptographic hash is required.      |
| Unsafe shell command          | Security (High)   | 60      | `os.system()` executes a shell command containing the receipt filename.                | Remove the shell command and use `print()` to display the success message. |
| Use of eval                   | Security (Medium) | 44      | `eval()` can execute arbitrary Python expressions.                                     | Replace it with a validated numeric discount parameter and a direct calculation. |
| Mutable default argument      | Bug               | 15      | `audit_log=[]` can share the same list across function calls.                          | Use `None` as the default and initialize a new list inside the function. |
| Bare exception                | Bug               | 26–29   | A bare `except` hides unexpected errors.                                               | Catch `KeyError` or handle missing items explicitly. |
| Insecure random generator     | Security (Low)    | 53      | `random.randint()` is unsuitable for security-sensitive PIN generation.                | Use `secrets.randbelow()` to generate a PIN. |
| Unused import                 | Code quality      | 4       | The imported `math` module is never used.                                              | Remove the unused import. |
| Unused variable               | Code quality      | 33      | `handling_fee` is assigned but never used.                                             | Remove it or implement the intended handling-fee calculation. |
| Incorrect None comparison     | Code quality      | 34      | The code compares a value to `None` using `==`.                                        | Replace it with `is None`. |
| File handling                 | Code quality      | 57–59   | The file is opened and closed manually without an explicit encoding.                   | Use `with open(filename, "w", encoding="utf-8")` for safe resource handling. |
| Missing final newline         | Style             | 84      | The Python file does not end with a newline.                                           | Add a newline at the end of the file. |
| Long line                     | Style             | 76      | A line exceeds Flake8's 79-character limit.                                            | Split the statement across multiple lines. |

