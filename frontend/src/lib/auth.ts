"use client";

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const MODE = process.env.NEXT_PUBLIC_AUTH_MODE === "supabase" ? "supabase" : "dev";
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEV_KEY = "sih.devToken";

let supabase: SupabaseClient | null = null;
function sb(): SupabaseClient {
  if (!supabase) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !key) throw new Error("Supabase is not configured.");
    supabase = createClient(url, key);
  }
  return supabase;
}

export const authMode = MODE;

function store(): Storage | null {
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export async function getToken(): Promise<string | null> {
  if (MODE === "supabase") {
    const { data } = await sb().auth.getSession();
    return data.session?.access_token ?? null;
  }
  return store()?.getItem(DEV_KEY) ?? null;
}

export async function signIn(email: string, password: string): Promise<void> {
  if (MODE === "supabase") {
    const { error } = await sb().auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
    return;
  }
  const r = await fetch(`${API}/dev/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!r.ok) throw new Error("Development sign-in is not available on this server.");
  store()?.setItem(DEV_KEY, (await r.json()).access_token);
}

export async function signUp(email: string, password: string): Promise<"signed-in" | "check-email"> {
  if (MODE === "supabase") {
    const { data, error } = await sb().auth.signUp({ email, password });
    if (error) throw new Error(error.message);
    return data.session ? "signed-in" : "check-email";
  }
  await signIn(email, password);
  return "signed-in";
}

export async function signOut(): Promise<void> {
  if (MODE === "supabase") await sb().auth.signOut();
  store()?.removeItem(DEV_KEY);
}
