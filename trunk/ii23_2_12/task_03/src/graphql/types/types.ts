import { User } from "@prisma/client";

export interface GraphQLContext {
  user: User | null;
}
