# Messages Table Schema

| Column            | Data Type   | Constraints          |
|-------------------|-------------|----------------------|
| message_id        | TEXT        | PRIMARY KEY           |
| campaign_id       | INTEGER     |                      |
| message_type      | TEXT        |                      |
| client_id         | INTEGER     |                      |
| channel           | TEXT        |                      |
| stream            | TEXT        |                      |
| date              | DATETIME    |                      |
| sent_at           | DATETIME    |                      |
| is_opened         | BOOLEAN     |                      |
| is_clicked        | BOOLEAN     |                      |
| is_unsubscribed   | BOOLEAN     |                      |
| is_complained     | BOOLEAN     |                      |
| is_blocked        | BOOLEAN     |                      |
| is_purchased      | BOOLEAN     |                      |
