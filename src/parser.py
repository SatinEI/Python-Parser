from bs4 import BeautifulSoup
import requests


class ForumParser:
    @staticmethod
    def parse_page(url: str):
        headers = {"User-Agent": "ForumParserLab/1.0"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        comment_tree = soup.find('table', class_='comment-tree')
        if comment_tree is None:
            return []

        parsed_data = []
        for comment in comment_tree.find_all('tr', class_='comtr'):
            comment_id = comment.get('id', '')
            comhead = comment.find(class_='comhead')
            user = comhead.find('a') if comhead else None
            text = comment.find(class_='commtext')
            if not comment_id.isdecimal() or user is None or text is None:
                continue
            parsed_data.append({
                "id": int(comment_id),
                "user": user.get_text(strip=True),
                "text": text.decode_contents(),
            })
        return parsed_data

    @staticmethod
    def save_to_db(parsed_data, repository):
        for comment in parsed_data:
            repository.add(comment["id"], comment["user"], comment["text"])
