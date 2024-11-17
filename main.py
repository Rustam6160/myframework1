import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import re


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/':
            content = self.generate_list_html('user_data')

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(content.encode('utf-8'))
        elif path == '/news':
            content = self.generate_list_html('news_data')

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(content.encode('utf-8'))
        elif '/newss_page' in path:
            newss_id = re.findall(r'\d+', path)
            print(newss_id)
            with open(f'data_base/news_data.json', 'r') as file:
                json_data = json.load(file)
            news = json_data.get('news', {})
            rows = "j"
            for n in news:
                if n['id'] == int(newss_id[0]):
                    news_id = n.get('id', 'Неизвестно')
                    title = n.get('title', 'Неизвестно')
                    content = n.get('content', 'Неизвестно')
                    author = n.get('author', 'Неизвестно')
                    date = n.get('date', 'Неизвестно')
                    rows = f"""
                    <form method="post" action="/change_news">
                        <input type="text" name="news_id" placeholder="news_id" value="{news_id}"><br>
                        <input type="text" name="title" placeholder="title" value="{title}"><br>
                        <input type="text" name="content" placeholder="content" value="{content}"><br>
                        <input type="text" name="author" placeholder="author" value="{author}"><br>
                        
                        <button type="submit">Изменить</button>
                    </form><br>    
                        """
                    break
            with open(f'html/newss_page.html', 'r', encoding='utf-8') as template_file:
                template = template_file.read()

            html = template.replace("{LIST}", rows)



            content = html

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(content.encode('utf-8'))

        else:
            self.send_error(404, 'page not found')

    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/reg':
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length)
            post_data = parse_qs(raw_post_data.decode('utf-8'))

            with open('data_base/user_data.json', 'r+') as file:
                json_data = json.load(file)

                new_data = {"id": json_data['users'][-1]['id']+1,
                            "username": post_data['username'][0],
                            "password": post_data['password'][0]}
                json_data['users'].append(new_data)
                file.seek(0)
                json.dump(json_data, file, indent=4)

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        elif path == '/create_news':
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length)
            post_data = parse_qs(raw_post_data.decode('utf-8'))

            with open('data_base/news_data.json', 'r+') as file:
                json_data = json.load(file)

                new_data = {"id": json_data['news'][-1]['id'] + 1,
                            "title": post_data['title'][0],
                            "content": post_data['content'][0],
                            "author": post_data['author'][0],
                            "date": str(datetime.today())}
                json_data['news'].append(new_data)
                file.seek(0)
                json.dump(json_data, file, indent=4)

            self.send_response(302)
            self.send_header('Location', '/news')
            self.end_headers()
        elif path == '/change_news':
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length)
            post_data = parse_qs(raw_post_data.decode('utf-8'))
            print(post_data)

            with open('data_base/news_data.json', 'r+') as file:
                json_data = json.load(file)

                new_data = {"id": int(post_data['news_id'][0]),
                            "title": post_data['title'][0],
                            "content": post_data['content'][0],
                            "author": post_data['author'][0],
                            "date": str(datetime.today())}
                json_data['news'][int(post_data['news_id'][0])-1] = new_data
                file.seek(0)
                json.dump(json_data, file, indent=4)

            self.send_response(302)
            self.send_header('Location', '/news')
            self.end_headers()


    def generate_list_html(self, data):
        try:
            with open(f'data_base/{data}.json', 'r') as file:
                json_data = json.load(file)
                if data == 'user_data':
                    html_file_name = 'index.html'
                    users = json_data.get('users', {})
                    rows = ""
                    for user in users:
                        user_id = user.get('id', 'Неизвестно')
                        username = user.get('username', 'Неизвестно')  # name = user_data['name']
                        rows += f"""
                        <tr>
                            <td>{user_id}</td>
                            <td>{username}</td>
                        </tr>
                        """
                elif data == 'news_data':
                    html_file_name = 'news.html'
                    news = json_data.get('news', {})
                    rows = ""
                    for n in news:
                        news_id = n.get('id', 'Неизвестно')
                        title = n.get('title', 'Неизвестно')
                        content = n.get('content', 'Неизвестно')
                        author = n.get('author', 'Неизвестно')
                        date = n.get('date', 'Неизвестно')
                        rows += f"""
                        <tr>
                            <td><a href="/newss_page{news_id}">{news_id}</a></td>
                            <td>{title}</td>
                            <td>{content}</td>
                            <td>{author}</td>
                            <td>{date}</td>
                        </tr>
                        """
                with open(f'html/{html_file_name}', 'r', encoding='utf-8') as template_file:
                    template = template_file.read()

                html = template.replace("{LIST}", rows)

                return html

        except FileNotFoundError:
            return "<html><body><h1>Ошибка: Файл данных не найден</h1></body></html>"
        except json.JSONDecodeError:
            return "<html><body><h1>Ошибка: Невозможно прочитать данные</h1></body></html>"


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f'Starting: http://localhost:{port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()