import { gql } from "graphql-tag";

export const typeDefs = gql`
  type Ad {
    id: ID!
    title: String!
    description: String!
    price: Int!
    images: [String!]!
    userId: ID!
  }

  type User {
    id: ID!
    ads: [Ad!]!
    email: String!
  }

  input RegisterInput {
    email: String!
    password: String!
  }

  input LoginInput {
    email: String!
    password: String!
  }

  input CreateAdInput {
    title: String!
    description: String!
    price: Int!
    images: [String!]!
  }

  type AuthPayload {
    token: String!
    user: User!
  }

  type Query {
    ads: [Ad!]!
    ad(id: ID!): Ad
    me: User
  }

  type Mutation {
    register(input: RegisterInput!): AuthPayload!
    login(input: LoginInput!): AuthPayload!
    createAd(input: CreateAdInput!): Ad!
    deleteAd(id: ID!): Boolean!
  }
`;
