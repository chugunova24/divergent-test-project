import os

from flask import Flask, jsonify, abort
from typing import Tuple
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII'] = False

PATH_JSONFILES = "data"


def read_json_file(filename: str) -> dict:
    """
    Чтение из json-файла и запись в словарь
    """
    path_to_file = PATH_JSONFILES + f"/{filename}"

    if os.path.getsize(path_to_file) == 0:
        return {}

    with open(path_to_file,
              "r",
              encoding="utf-8") as json_posts:
        result = json.load(json_posts)

    return result


def data_loader() -> Tuple[dict, dict]:
    """
    Функция загружает данные из json файлов и преобразует их в dict.
    Функция не должна нарушать изначальную структуру данных.
    """
    posts = read_json_file(filename="posts.json")
    comments = read_json_file(filename="comments.json")

    return posts, comments


@app.route("/")
def get_posts():
    """
    На странице / вывести json в котором каждый элемент - это:
    - пост из файла posts.json.
    - для каждой поста указано кол-во комментариев этого поста из файла comments.json

    Формат ответа:
    posts: [
        {
            id: <int>,
            title: <str>,
            body: <str>, 
            author:	<str>,
            created_at: <str>,
            comments_count: <int>
        }
    ],
    total_results: <int>

    Порядок ключей словаря в ответе не важен
    """
    posts, comments = data_loader()
    counter = {}

    for comment in comments.get("comments", {}):
        post_id = str(comment["post_id"])
        if post_id in counter:
            counter[post_id] += 1
        else:
            counter[post_id] = 1

    for post in posts.get("posts", {}):
        post_id = str(post["id"])
        post["comments_count"] = int(counter.get(post_id, 0))

    return jsonify(posts)


@app.route("/posts/<int:post_id>")
def get_post(post_id):
    """
    На странице /posts/<post_id> вывести json, который должен содержать:
    - пост с указанным в ссылке id
    - список всех комментариев к новости

    Отдавайте ошибку abort(404), если пост не существует.


    Формат ответа:
    id: <int>,
    title: <str>,
    body: <str>, 
    author:	<str>,
    created_at: <str>
    comments: [
        "user": <str>,
        "post_id": <int>,
        "comment": <str>,
        "created_at": <str>
    ]

    Порядок ключей словаря в ответе не важен
    """
    posts, comments = data_loader()
    output = {}

    for post in posts["posts"]:
        if post["id"] == post_id:
            output.update(post)
            break
    if not output:
        return abort(404)

    output["comments"] = []
    for comment in comments["comments"]:
        if comment["post_id"] == post_id:
            output["comments"].append(comment)

    return jsonify(output)
