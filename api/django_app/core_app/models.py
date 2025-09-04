from django.db import models

class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True, verbose_name="用戶唯一識別碼")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

class UserInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inputs")
    input_text = models.TextField(verbose_name="用戶輸入")
    ai_response = models.TextField(null=True, blank=True, verbose_name="AI 回覆")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} - {self.input_text[:20]}"