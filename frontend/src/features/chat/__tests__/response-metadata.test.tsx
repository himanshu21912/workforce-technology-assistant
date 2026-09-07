import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ResponseMetadata } from "@/features/chat/components/response-metadata";

describe("ResponseMetadata", () => {
  it("labels a PostgreSQL-backed answer and its tools", () => {
    render(
      <ResponseMetadata
        metadata={{
          source: "postgresql",
          tools_used: ["search_employees", "get_employee_details"],
          cache_hit: false,
          similarity_score: null,
          model_name: "qwen3:8b",
        }}
      />,
    );

    expect(screen.getByText("Internal workforce data")).toBeInTheDocument();
    expect(screen.getByText("Employee search")).toBeInTheDocument();
    expect(screen.getByText("Employee details")).toBeInTheDocument();
    expect(screen.getByText("Model: qwen3:8b")).toBeInTheDocument();
    expect(screen.queryByText("Semantic cache")).not.toBeInTheDocument();
  });

  it("labels GitHub, multi-source and general-knowledge answers", () => {
    const { rerender } = render(
      <ResponseMetadata
        metadata={{ source: "github_mcp", tools_used: ["search_github_repositories"] }}
      />,
    );

    expect(screen.getByText("Current GitHub data")).toBeInTheDocument();
    expect(screen.getByText("GitHub search")).toBeInTheDocument();

    rerender(
      <ResponseMetadata metadata={{ source: "multi_source", tools_used: [] }} />,
    );
    expect(screen.getByText("Workforce + GitHub")).toBeInTheDocument();

    rerender(<ResponseMetadata metadata={{ source: "llm", tools_used: [] }} />);
    expect(screen.getByText("General knowledge")).toBeInTheDocument();
  });

  it("shows the semantic cache badge with the similarity percentage", () => {
    render(
      <ResponseMetadata
        metadata={{
          source: "postgresql",
          tools_used: [],
          cache_hit: true,
          similarity_score: 0.96,
        }}
      />,
    );

    expect(screen.getByText(/Semantic cache/)).toBeInTheDocument();
    expect(screen.getByText("· 96% match")).toBeInTheDocument();
  });

  it("renders nothing when there is no metadata to show", () => {
    const { container } = render(<ResponseMetadata metadata={{}} />);

    expect(container).toBeEmptyDOMElement();
  });
});
