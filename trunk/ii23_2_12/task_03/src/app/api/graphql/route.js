import { startServerAndCreateNextHandler } from "@as-integrations/next";
import { ApolloServer } from "@apollo/server";
import { typeDefs } from "@/graphql/schema/typeDefs";
import { resolvers } from "@/graphql/schema/resolvers";
import { verifyToken } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const server = new ApolloServer({
  typeDefs,
  resolvers,
});

const handler = startServerAndCreateNextHandler(server, {
  context: async (req) => {
    const authHeader = req.headers.get("authorization");
    const token = authHeader?.replace("Bearer ", "");
    const decoded = token ? verifyToken(token) : null;

    const user = decoded?.userId
      ? await prisma.user.findUnique({ where: { id: decoded.userId } })
      : null;

    return { user };
  },
});

export { handler as GET, handler as POST };
