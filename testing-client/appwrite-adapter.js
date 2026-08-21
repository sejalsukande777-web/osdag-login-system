(function () {
  function appwriteModeOn() {
    const radios = document.getElementsByName("backendMode");
    for (const r of radios) if (r.value === "appwrite" && r.checked) return true;
    return false;
  }

  function cfg() {
    return {
      endpoint: document.getElementById("awEndpoint").value,
      projectId: document.getElementById("awProjectId").value,
      databaseId: document.getElementById("awDatabaseId").value,
      filesCollectionId: document.getElementById("awFilesCollectionId").value,
    };
  }

  function client() {
    const c = cfg();
    const cl = new Appwrite.Client().setEndpoint(c.endpoint).setProject(c.projectId);
    return {
      account: new Appwrite.Account(cl),
      databases: new Appwrite.Databases(cl),
      c,
    };
  }

  function json(status, body) {
    return new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });
  }

  async function handleRegister(req) {
    const { account } = client();
    const { email, password } = await req.json();
    try {
      const user = await account.create(Appwrite.ID.unique(), email, password);
      return json(201, { id: user.$id, email: user.email });
    } catch (e) {
      return json(e.code || 400, { error: e.message });
    }
  }

  async function handleLogin(req) {
    const { account } = client();
    const { email, password } = await req.json();
    try {
      const session = await account.createEmailPasswordSession(email, password);
      const user = await account.get();
      return json(200, {
        token: session.$id,
        user: { id: user.$id, email: user.email },
      });
    } catch (e) {
      return json(e.code || 401, { error: e.message });
    }
  }

  async function handleLogout() {
    const { account } = client();
    try {
      await account.deleteSession("current");
      return json(200, { message: "Logged out" });
    } catch (e) {
      return json(e.code || 400, { error: e.message });
    }
  }

  async function handleMe() {
    const { account } = client();
    try {
      const user = await account.get();
      return json(200, { id: user.$id, email: user.email, profile: { fullName: user.name } });
    } catch (e) {
      return json(401, { error: "Not authenticated" });
    }
  }

  async function handleFiles() {
    const { account, databases, c } = client();
    try {
      const me = await account.get();
      const res = await databases.listDocuments(c.databaseId, c.filesCollectionId, [
        Appwrite.Query.equal("owner_id", me.$id),
      ]);
      const files = res.documents.map((d) => ({
        id: d.$id,
        ownerId: d.owner_id,
        fileName: d.filename,
        mimeType: "text/plain",
        sizeBytes: (d.content || "").length,
        uploadedAt: d.$createdAt,
      }));
      return json(200, { files });
    } catch (e) {
      return json(e.code || 401, { error: e.message || "Not authenticated" });
    }
  }

  async function handleFileById(fileId) {
    const { account, databases, c } = client();
    try {
      const me = await account.get();
      const doc = await databases.getDocument(c.databaseId, c.filesCollectionId, fileId);
      if (doc.owner_id !== me.$id) {
        return json(403, { error: "You do not have access to this file" });
      }
      return json(200, {
        file: {
          id: doc.$id,
          ownerId: doc.owner_id,
          fileName: doc.filename,
          mimeType: "text/plain",
          sizeBytes: (doc.content || "").length,
          uploadedAt: doc.$createdAt,
        },
      });
    } catch (e) {
      return json(e.code || 404, { error: e.message || "File not found" });
    }
  }

  const previousFetch = window.fetch.bind(window);

  window.fetch = async function (input, init) {
    if (!appwriteModeOn()) return previousFetch(input, init);

    const url = typeof input === "string" ? input : input.url;
    const { pathname } = new URL(url, window.location.href);
    const req = new Request(url, init);

    if (pathname === "/register" && req.method === "POST") return handleRegister(req);
    if (pathname === "/login" && req.method === "POST") return handleLogin(req);
    if (pathname === "/logout" && req.method === "POST") return handleLogout();
    if (pathname === "/me" && req.method === "GET") return handleMe();
    if (pathname === "/files" && req.method === "GET") return handleFiles();

    const m = pathname.match(/^\/files\/([^/]+)$/);
    if (m && req.method === "GET") return handleFileById(m[1]);

    return previousFetch(input, init);
  };

  console.info("[appwrite-adapter] ready");
})();
