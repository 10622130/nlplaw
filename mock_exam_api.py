from http.server import HTTPServer, BaseHTTPRequestHandler
import json

MOCK_RESPONSE = json.dumps({
    "question": (
        "【測試題目】依民法規定，契約之要約，其要約定有承諾期限者，下列敘述何者正確？\n"
        "(A) 要約人得撤回要約\n"
        "(B) 要約人於期限內不得撤銷要約\n"
        "(C) 要約人得隨時撤銷要約\n"
        "(D) 要約於期限屆滿後仍然有效"
    ),
    "answer": "B",
}, ensure_ascii=False).encode()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(MOCK_RESPONSE)

    def log_message(self, fmt, *args):
        print(f"[mock-exam] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
