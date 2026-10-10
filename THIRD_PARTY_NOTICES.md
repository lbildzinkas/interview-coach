# Third-party notices

This repository commits no third-party study material. `coach setup` downloads
it, at the commits pinned in [`sources.yaml`](sources.yaml), into the
git-ignored `data/study-material/` folder (see
[ADR-0002](docs/adr/0002-personal-data-and-study-material-stay-out-of-the-repo.md)).
Anything the coach derives from it, such as quotes, citations or question
cards, carries the credit below.

## The System Design Primer

- Source: https://github.com/donnemartin/system-design-primer
- Used: the README text, the worked solutions and the Anki decks; no images
- Copyright 2017 Donne Martin
- Licence: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

## Tech Interview Handbook

- Source: https://github.com/yangshun/tech-interview-handbook
- Used: selected pages from `apps/website/contents/`

```text
MIT License

Copyright (c) 2017-Present Yangshun Tay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Machine Learning Interviews

- Source: https://github.com/alirezadir/Machine-Learning-Interviews
- Used: the English guides under `src/` and the README; no translations or notebooks
- Copyright (c) 2021 Alireza Dirafzoon
- Licence: MIT, with the [MIT permission notice](#mit-permission-notice) below

## Generative AI for Beginners

- Source: https://github.com/microsoft/generative-ai-for-beginners
- Used: the English lesson pages; no translations, images or code samples
- Copyright (c) Microsoft Corporation.
- Licence: MIT, with the [MIT permission notice](#mit-permission-notice) below

## AI Agents for Beginners

- Source: https://github.com/microsoft/ai-agents-for-beginners
- Used: the English lesson pages and study guide; no translations, images or code samples
- Copyright (c) Microsoft Corporation.
- Licence: MIT, with the [MIT permission notice](#mit-permission-notice) below

## MIT permission notice

The permission notice that comes with each MIT copyright line above:

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## LLM Course

- Source: https://github.com/mlabonne/llm-course
- Used: the course README; no images
- Author: Maxime Labonne
- Licence: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0); the repository has no NOTICE file

## Hugging Face Agents Course

- Source: https://github.com/huggingface/agents-course
- Used: selected English units under `units/en/`; no other languages or images
- Author: Hugging Face
- Licence: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0); the repository has no NOTICE file

## Read-only references (local only)

These repositories have no licence, so all rights stay with their authors.
`coach setup` downloads them for personal study on this machine only
(`local_only: true` in `sources.yaml`). Nothing from them, quoted or derived,
is committed or shared.

- AI Engineering Field Guide, by Alexey Grigorev: https://github.com/alexeygrigorev/ai-engineering-field-guide
  (the interview chapters and the question bank)
- Introduction to Machine Learning Interviews, Copyright ©2021 Chip Huyen: https://github.com/chiphuyen/ml-interviews-book
  (the interview process and the questions)
- AI Engineering book resources, by Chip Huyen: https://github.com/chiphuyen/aie-book
  (the table of contents, chapter summaries, study notes, resources and prompt examples)
