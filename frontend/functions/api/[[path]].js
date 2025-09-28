// frontend/functions/api/[[path]].js
export async function onRequest(context) {
  // URL original (p. ej. https://<preview>.pages.dev/api/token/)
  const incoming = new URL(context.request.url);

  // Construimos la URL destino en el backend público
  const target = new URL(incoming.toString());
  target.hostname = "api.appquaculture.com";
  target.protocol = "https:";

  // Si tu backend NO usara prefijo /api, quitarlo:
  // target.pathname = target.pathname.replace(/^\/api/, "");

  // Reenviamos método, headers y body tal cual
  const forwardReq = new Request(target.toString(), {
    method: context.request.method,
    headers: context.request.headers,
    body: ["GET", "HEAD"].includes(context.request.method)
      ? undefined
      : context.request.body,
    redirect: "manual",
  });

  return fetch(forwardReq);
}
