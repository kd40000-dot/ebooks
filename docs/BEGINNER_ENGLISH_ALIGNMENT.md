# I Found a Unicorn — beginner-friendly English alignment

This edition deliberately **does not modify any Vietnamese text or hyphenation**. It revises English to make Vietnamese expressions easier to recognize while preserving the supplied story's meaning.

## Approach

1. Natural Vietnamese and 155 existing contextual hyphen connections are frozen.
2. Original English is retained byte-for-byte in `english_original_reference.txt`.
3. English is rewritten against the Vietnamese first, checked against original English second.
4. Paragraph counts: 16 Vietnamese / 16 revised English. Matching sentence-ending punctuation counts for all 16 paragraphs (heuristic; test in Smart Book).
5. The existing three chapters retain their original 5 / 5 / 6 paragraph split and numbered titles.
6. App setting: Vietnamese primary; revised English as attached translation; End of sentence; approved cover JPEG. No chapter illustrations.
7. The earlier tested three-chapter and cover-enabled editions are left unchanged on their recovery branches.

## Specific examples

| Fixed Vietnamese | Earlier English | Revised learner English |
|---|---|---|
| Chào mọi người trên Reddit. | Hello, Reddit. | Hello, everyone on Reddit. |
| Để tôi kể từ đầu. | Let's start from the beginning. | Let me tell you what happened from the beginning. |
| Tôi đứng chết-lặng, không biết phải làm gì. | I stood there in shock, unsure what to do. | I stood frozen, not knowing what to do. |
| Đã mấy ngày trôi-qua mà không có thêm vụ án-mạng nào. | It's been several days and no more murders have occurred. | Several days have passed without any more murders. |

## Validation status

The input edits and exact chapter segmentation are validated in repository source. A new native Smart Book SB2 must be exported and then tested on the user's Fairphone to confirm the learner-oriented English aligns well in the app's sentence-translation interface.
