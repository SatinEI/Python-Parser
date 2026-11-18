from pathlib import Path

from src.database import DatabaseRepository
from src.parser import ForumParser


def main():
    parser = ForumParser()
    repository = DatabaseRepository(str(Path(__file__).with_name('comments.db')))
    try:
        comments = parser.parse_page('https://news.ycombinator.com/item?id=50341174')
        print(f'Получено комментариев: {len(comments)}')
        new_comments = [comment for comment in comments
                        if repository.get_by_id(comment['id']) is None]
        parser.save_to_db(new_comments, repository)
        print(f'Добавлено в SQLite: {len(new_comments)}')
        if comments:
            print(repository.get_by_id(comments[0]['id']))
    finally:
        repository.connection.close()


if __name__ == '__main__':
    main()
