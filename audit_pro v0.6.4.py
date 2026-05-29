"""
Pai Nayak & Associates - Audit Management Software
Primary file extension: .pna (PNA Audit File); legacy .caf files supported
Fully offline Windows desktop application

Thin launcher. All application code lives in the `audit_pro` package.
"""
from audit_pro.app import main

if __name__ == "__main__":
    main()
