import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";
import { signToken } from "@/lib/auth";
import { Ad, User } from "@prisma/client";
import { GraphQLContext } from "../types/types";

export const resolvers = {
  Query: {
    ads: async (): Promise<Ad[]> => {
      return prisma.ad.findMany();
    },
    ad: async (_: unknown, { id }: { id: String }) => {
      try {
        const ad = await prisma.ad.findUnique({ where: { id: String(id) } });
        if (!ad) {
          throw new Error("Ad not found");
        }
        return ad;
      } catch (error) {
        console.error("Error fetching ad:", error);
        throw new Error("Error fetching ad");
      }
    },
    me: async (
      _: unknown,
      __: unknown,
      context: GraphQLContext
    ): Promise<User | null> => {
      return context.user;
    },
  },

  Mutation: {
    register: async (
      _: unknown,
      { input }: { input: { email: string; password: string } }
    ): Promise<{ token: string; user: User }> => {
      const hashed = await bcrypt.hash(input.password, 10);
      const user = await prisma.user.create({
        data: { email: input.email, password: hashed },
      });

      return { token: signToken(user.id), user };
    },

    login: async (
      _: unknown,
      { input }: { input: { email: string; password: string } }
    ): Promise<{ token: string; user: User }> => {
      const user = await prisma.user.findUnique({
        where: { email: input.email },
      });

      if (!user || !(await bcrypt.compare(input.password, user.password))) {
        throw new Error("Invalid credentials");
      }

      return { token: signToken(user.id), user };
    },

    createAd: async (
      _: unknown,
      {
        input,
      }: {
        input: {
          title: string;
          description: string;
          price: number;
          images: string[];
        };
      },
      context: GraphQLContext
    ): Promise<Ad> => {
      const { user } = context;
      if (!user) throw new Error("Unauthorized");

      return prisma.ad.create({
        data: {
          ...input,
          user: { connect: { id: user.id } },
        },
      });
    },

    deleteAd: async (
      _: unknown,
      { id }: { id: string },
      context: GraphQLContext
    ): Promise<boolean> => {
      const { user } = context;
      if (!user) throw new Error("Unauthorized");

      const ad = await prisma.ad.findUnique({ where: { id } });
      if (!ad || ad.userId !== user.id) {
        throw new Error("Not found or forbidden");
      }

      await prisma.ad.delete({ where: { id } });
      return true;
    },
  },

  User: {
    ads: (parent: User): Promise<Ad[]> => {
      return prisma.ad.findMany({ where: { userId: parent.id } });
    },
  },
};
