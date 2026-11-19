import { createContext, useContext } from "react";

import type { User } from "@/lib/api";

/**
 * Профиль загружается один раз в оболочке приложения, а страницы берут его
 * отсюда: иначе каждая страница дёргала бы `/users/me` заново.
 */
export const ProfileContext = createContext<User | null>(null);

export function useProfile(): User | null {
  return useContext(ProfileContext);
}
