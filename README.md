# RAG over Legal & Regulatory Documents — Demo

## What this is

A small app that answers questions about Vietnam import-export tax regulations by:
1. Searching a set of regulation excerpts for the most relevant article
2. If a confident match is found — answering with a citation (document + article)
3. If no confident match is found — saying so honestly, instead of guessing

## What I chose and why

I chose **Option 3: RAG over Legal & Regulatory Documents** because it builds
directly on architecture I already have experience with (React frontend,
Node/Express-style backend, database-backed storage) from my e-learning
platform project. This let me focus my limited time on the part that matters
most: deciding when to answer confidently versus when to abstain.

## Document source

The source content is adapted from **Circular No. 113/2005/TT-BTC**, issued
by Vietnam's Ministry of Finance, guiding the implementation of the Import
Tax and Export Tax Law. The original English translation is hosted publicly
by the WTO as part of Vietnam's accession documents:
https://www.wto.org/english/thewto_e/acc_e/vnm_e/wtaccvnm44a1_leg_2.pdf

The provisions in `backend/documents/` are my own concise summaries of
specific real articles from this circular (covering taxable goods, payment
deadlines, exchange rates, gift tax exemptions, refunds, and complaints),
each labeled with the actual Part/Section of the original circular so the
citation is verifiable against the real source.

## What already existed vs. what I built

- **Existing knowledge reused:** general backend/frontend architecture
  pattern from my e-learning platform project (separate frontend, backend,
  database rather than files in memory).
- **Built for this assignment:** the document chunking and storage logic,
  the confidence-scoring retrieval function, the abstain threshold logic,
  the Flask API endpoint, the React frontend, and the Gemini AI integration.

## How it works

1. Regulatory text is split into article-level chunks and stored in a
   SQLite database (`backend/database.py`).
2. When a question comes in, `backend/retrieve.py` scores every chunk by
   keyword overlap with the question (ignoring common words, including
   domain words like "tax" and "import" that appear in nearly every
   article and don't help distinguish topics) and picks the best match.
3. If the best match's score is below a confidence threshold (0.55), the
   app returns "not found" instead of guessing.
4. If confident, the matched text is sent to Google's Gemini model along
   with the question, and the model's answer is returned with a citation
   (document name + article).

## How to run it

### Backend
```bash
cd backend
pip install -r requirements.txt
python database.py       # sets up the database with the sample documents
export GEMINI_API_KEY="your-real-key-here"   # get a free key at https://aistudio.google.com/app/apikey
python app.py             # starts the API on http://localhost:5000
```

### Frontend
Open `frontend/index.html` directly in a browser. It uses React loaded via
CDN, so no npm install or build step is required. Make sure the backend is
running first.

## Results

Tested on 15 questions against the live `retrieve_best_match()` function:
**9 correctly matched with citation, 4 correctly abstained, 2 incorrect
matches, 0 fabricated citations** (every citation returned quoted real
source text — the two errors were wrong/missed *matches*, not made-up
content).

## Results

Tested against 8 questions using the live retrieve_best_match() function:
6 correctly matched with citation, 2 correctly abstained, 0 fabricated
citations.

1. How is customs value converted to Vietnamese Dong?
   Matched — Article 1 (Exchange Rate), score 0.60

2. What is the time limit for paying export tax?
   Matched — Article 3 (Export Tax Payment Time Limit), score 0.67

3. What is the tax exemption threshold for gifts to individuals?
   Matched — Article 2 (Gifts to Individuals), score 0.75

4. Are goods re-exported to a foreign owner eligible for a tax refund?
   Matched — Article 4 (Refund for Re-Exported Goods), score 0.80

5. Are machinery temporarily imported for ODA projects exempt from tax?
   Matched — Article 2 (ODA Temporary Import), score 0.83

6. Can goods brought into a non-tariff zone be taxed?
   Matched — Article 1 (Taxable Objects), score 0.60

7. What is the tax rate for coffee exports?
   Correctly abstained (not in documents), score 0.33

8. How long is an import license valid for foreign-funded projects?
   Correctly abstained (not in documents), score 0.20

Known limitation: the scoring is pure keyword overlap, so it can confuse
similarly-worded articles (e.g. "gifts to individuals" vs. "gifts to
organizations" score almost identically) or miss a relevant article when
a question uses mostly stopwords. Real embeddings would address this —
see "What I would improve" below.

**Notable failure modes observed:**
- **Question 4** shows the keyword-overlap approach can't distinguish
  "individuals" vs. "organizations" once the shared words ("tax exemption
  threshold", "gifts") dominate the score — a case where real embeddings
  would likely do better.
- **Question 7** shows a question made almost entirely of stopwords/domain
  words (goods, import, export, tax) can leave too little signal to match,
  even though a relevant article exists.

## What I would improve with more time

- Replace the keyword-overlap scoring with real embeddings/vector search
  for more accurate semantic matching (currently it can miss paraphrased
  questions that don't share exact words with the source text, or
  conflate similar articles — see Results above)
- Move from SQLite to PostgreSQL to match my existing project stack
- Add a proper build setup for the React frontend instead of loading it via
  CDN, and add loading/error states
- Support PDF documents directly instead of manually summarized text
- Expand the document set to cover more of the circular's provisions
- Move the API key and other config into a `.env` file with a secrets
  manager for anything beyond a single local demo