import { getUserFromToken } from "@/lib/auth";

export async function createContext({ request }: { request: Request }) {
  const authHeader = request.headers.get("authorization") || "";
  const token = authHeader.replace("Bearer ", "");
  const user = await getUserFromToken(token);
  return { user };
}
