import { NextRequest, NextResponse, userAgent } from "next/server";

/** Remembers an explicit choice of view: "3d" or "simple". */
const VIEW_COOKIE = "view";

/**
 * Phones get the simple view (/lite) by default: the 3D world downloads
 * several MB of models and needs a real GPU. Deciding here, on the server,
 * means a phone never starts that download just to be sent away.
 *
 * The choice is the visitor's to override, and it sticks:
 *   /?view=3d      -> remember "3d", show the 3D world (any device)
 *   /?view=simple  -> remember "simple", show /lite
 * Tablets and desktops get the 3D world unless they chose "simple".
 */
export function middleware(req: NextRequest) {
  const asked = req.nextUrl.searchParams.get("view");
  if (asked === "3d" || asked === "simple") {
    const res = NextResponse.redirect(new URL(asked === "3d" ? "/" : "/lite", req.url));
    res.cookies.set(VIEW_COOKIE, asked, { path: "/", maxAge: 60 * 60 * 24 * 30, sameSite: "lax" });
    return res;
  }

  const chosen = req.cookies.get(VIEW_COOKIE)?.value;
  if (chosen === "3d") return NextResponse.next();
  if (chosen === "simple" || userAgent(req).device.type === "mobile") {
    return NextResponse.redirect(new URL("/lite", req.url));
  }
  return NextResponse.next();
}

export const config = { matcher: "/" };
