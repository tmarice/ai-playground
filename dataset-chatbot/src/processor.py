import duckdb
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage

from src.datasource import DataSource
from src.models import (AnswerStrategy, ProcessorResponse, SQLQueryOutput,
                        StrategyDecision)
from src.sql_validator import SQLValidator


class DummyProcessor:
    def process(self, question: str, datasources: list[DataSource]) -> str:
        """Process a question against the loaded datasets.

        Args:
            question: The user's question
            datasources: List of loaded DataSource objects

        Returns:
            A dummy response string
        """
        dataset_info = []
        for ds in datasources:
            dataset_info.append(
                f"  - {ds.name}: {ds.row_count} rows, {len(ds.columns)} columns"
            )

        info_str = "\n".join(dataset_info) if dataset_info else "  (no datasets loaded)"

        return (
            f"[Dummy Response]\nQuestion: '{question}'\nAvailable datasets:\n{info_str}"
        )


class DuckDBProcessor:
    DUCKDB_DOCS_URL = "https://raw.githubusercontent.com/duckdb/duckdb-web/refs/heads/main/docs/stable/sql/introduction.md"

    DECISION_PROMPT = """You are an expert data analyst. Your task is to decide if you can answer the user's query
    using only the dataset's metadata, or if you need to run a SQL query on the dataset.

    Here is the dataset metadata:
    {datasource_metadata}
    """

    SQL_QUERY_PROMPT = """You're an expert data analyst. Generate DuckDB compatible SQL which will answer the user's 
    question. Use only SELECTs, JOINs and aggregation functions. Do not alter the dataset in any way.

    User question:
    {question}

    Datasource metadata:
    {datasource_metadata}
    """

    MODEL = "gpt-5-nano"

    def __init__(self, datasources: list[DataSource]):
        self._datasources = datasources
        self.model = init_chat_model(self.MODEL)

    def process(self, question: str) -> str:
        # 1. Determine if we even need to generate a SQL query
        datasource_metadata = "\n\n".join(ds.metadata for ds in self._datasources)
        decision_prompt = self.DECISION_PROMPT.format(
            datasource_metadata=datasource_metadata
        )
        messages = [
            SystemMessage(decision_prompt),
            HumanMessage(question),
        ]
        response = self.model.with_structured_output(StrategyDecision).invoke(messages)
        messages.append(AIMessage(response.reason))

        if response.strategy == AnswerStrategy.METADATA:
            messages.append(
                HumanMessage(f"""Answer this question using the provided datasource metadata:
                    Question: 
                    {question}

                    Datasource Metadata: 
                    {datasource_metadata}
                    """)
            )

            response = self.model.with_structured_output(ProcessorResponse).invoke(
                messages
            )

            return response

        # 2. Cannot answer from metadata only, need to generate a SQL query
        else:
            # 2.1 Generate the appropriate query with given metadata
            sql_query_prompt = self.SQL_QUERY_PROMPT.format(
                question=question, datasouce_metadata=datasource_metadata
            )
            messages = [SystemMessage(sql_query_prompt)]
            response = self.model.with_structured_output(SQLQueryOutput).invoke(
                messages
            )

            # 2.2 Validate the generated SQL
            # TODO If contains errors, re-run the stage
            SQLValidator.validate(response.sql)

            # 2.3. Load the data into DuckDB
            for ds in self._datasources:
                duckdb.read_csv(ds._filepath)

            # 2.4 Run SQL
            result = duckdb.sql(response.sql)

            return result
