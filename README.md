[# 🔐 Secure Document Anonymization System

A full-stack academic paper management system built with **React**, **Django**, and **MySQL**, designed for secure document anonymization, peer review, and reversible author identity restoration. Developed as part of the Software Lab II course at Kocaeli University.

---

## 🚀 Features

### 📝 Author Panel
- Upload academic articles in PDF format.
- Automatic anonymization of:
  - Names
  - Emails
  - Institutional affiliations
- Anonymized author data is encrypted and stored securely.
- Authors can view the status of their submissions.

### 🧑‍⚖️ Editor Panel
- View all uploaded and anonymized articles.
- Assign reviewers based on article topic classification.
- View reviewer evaluations and make final decisions (Accept/Reject).
- Restore original author details (name, contact, affiliation) *precisely in-place* with original formatting (font, size, coordinates).

### 🕵️ Reviewer Panel
- Browse and download anonymized articles.
- Submit evaluation reports.
- Evaluations are appended to the end of the article PDF.

---

## 🔒 Anonymization Engine

The system uses `spaCy` + custom heuristics to detect:
- `PERSON`, `EMAIL`, `ORG`, and `GPE` entities.
- Handles uppercase names (e.g., "MOHAMMAD ASIF") with pattern-based matching.
- Stores encrypted metadata as JSON including:
  - Page number
  - Bounding box (`x0`, `y0`, `x1`, `y1`)
  - Font name
  - Font size
  - Line number

Anonymized words are replaced in-place with the word `ANONYMIZED`.

---

## 🔁 Reversible De-Anonymization

The editor can securely restore redacted author information using the encrypted metadata:
- Data is decrypted using `Fernet`.
- Text is reinserted at the exact original position with matching font and size.
- Both small inline elements and larger blocks are accurately restored.

---

## 🛠️ Technologies Used

| Layer           | Stack                |
|----------------|----------------------|
| Frontend       | React + Bootstrab    |
| Backend        | Django REST Framework |
| Database       | MySQL                |
| NLP            | spaCy + Custom Logic |
| PDF Handling   | PyMuPDF (fitz)       |
| Security       | Fernet (Symmetric Encryption) |

---

## ⚙️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/secure-document-anonymization.git](https://github.com/Ahmed-Bakier/DocumentAnonymizer.git)
   cd secure-document-anonymization
](https://github.com/Ahmed-Bakier/DocumentAnonymizer.git)
