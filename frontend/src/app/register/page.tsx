"use client";

import { useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { describeError, login, register } from "@/lib/api";
import { getToken, setToken } from "@/lib/token";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (getToken()) {
      router.replace("/");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (username.trim().length === 0 || password.length === 0) {
      setError("Введите логин и пароль");
      return;
    }

    setPending(true);
    try {
      await register({ username: username.trim(), password });

      // Регистрация не возвращает токен, поэтому сразу входим теми же данными.
      const response = await login(username.trim(), password);
      setToken(response.access_token);
      router.replace("/");
    } catch (requestError) {
      setError(describeError(requestError));
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-12">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Регистрация</CardTitle>
          <CardDescription>Аккаунт нужен, чтобы хранить свои материалы</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div className="space-y-1.5">
              <Label htmlFor="username">Логин</Label>
              <Input
                id="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                disabled={pending}
              />
              <p className="text-xs text-muted-foreground">
                От 3 до 64 символов: латиница, цифры, «_», «.», «-»
              </p>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="new-password"
                disabled={pending}
              />
              <p className="text-xs text-muted-foreground">Не короче 8 символов</p>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            <Button type="submit" className="w-full" disabled={pending}>
              {pending ? "Создаём аккаунт…" : "Зарегистрироваться"}
            </Button>

            <p className="text-center text-sm text-muted-foreground">
              Уже есть аккаунт?{" "}
              <Link href="/login" className="text-primary underline-offset-4 hover:underline">
                Войти
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
