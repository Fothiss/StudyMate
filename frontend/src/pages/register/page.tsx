import { Loader2, UserPlus } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { AuroraField } from "@/components/aurora-field";
import { Brand } from "@/app/shell/brand";
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
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (getToken()) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

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
      navigate("/", { replace: true });
    } catch (requestError) {
      setError(describeError(requestError));
    } finally {
      setPending(false);
    }
  }

  return (
    <main className="relative flex flex-1 items-center justify-center px-4 py-12">
      <AuroraField />

      <div className="rise w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Brand />
        </div>

        <Card className="glass aurora-border border-0 ring-0">
          <CardHeader>
            <CardTitle className="font-heading text-xl">Регистрация</CardTitle>
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
                {pending ? (
                  <>
                    <Loader2 className="size-4 animate-spin" aria-hidden />
                    Создаём аккаунт…
                  </>
                ) : (
                  <>
                    <UserPlus className="size-4" aria-hidden />
                    Зарегистрироваться
                  </>
                )}
              </Button>

              <p className="text-center text-sm text-muted-foreground">
                Уже есть аккаунт?{" "}
                <Link to="/login" className="text-primary underline-offset-4 hover:underline">
                  Войти
                </Link>
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
