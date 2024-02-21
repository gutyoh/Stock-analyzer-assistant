from hstest import dynamic_test, StageTest, CheckResult, TestedProgram
import re


class StockAnalyzerAssistantTest(StageTest):
    # Regular expressions for ID formats
    assistant_id_regex = r"asst_[A-Za-z0-9]{24}"
    thread_id_regex = r"thread_[A-Za-z0-9]{24}"
    run_id_regex = r"run_[A-Za-z0-9]{24}"

    assistant_name = "stock_analyzer_assistant"

    @dynamic_test(time_limit=60000)
    def test_assistant_handling(self):
        program = TestedProgram()
        output = program.start().strip()

        # Check for the presence of any assistant related message
        new_assistant_message = (f"No matching `{self.assistant_name}` assistant found, "
                                 f"creating a new assistant with ID:")
        existing_assistant_message = (f"Matching `{self.assistant_name}` assistant found, "
                                      f"using the first matching assistant with ID:")

        # Check for the presence of any assistant related message
        if new_assistant_message not in output and existing_assistant_message not in output:
            return CheckResult.wrong(
                f"Expected a message indicating either a new assistant creation or an existing assistant usage, "
                f"but none was found.\n"
                f"Your output: {output}"
            )

        # Validate the format of the IDs
        if not re.search(self.assistant_id_regex, output):
            return CheckResult.wrong(
                "The assistant ID does not match the expected format.\n" +
                f"Expected format: {self.assistant_id_regex}\n" +
                f"Your output: {output}"
            )

        if not re.search(self.thread_id_regex, output):
            return CheckResult.wrong(
                "The thread ID does not match the expected format.\n" +
                f"Expected format: {self.thread_id_regex}\n" +
                f"Your output: {output}"
            )

        if not re.search(self.run_id_regex, output):
            return CheckResult.wrong(
                "The run ID does not match the expected format.\n" +
                f"Expected format: {self.run_id_regex}\n" +
                f"Your output: {output}"
            )

        return CheckResult.correct()


if __name__ == '__main__':
    StockAnalyzerAssistantTest('stock_analyzer_assistant.stock_analyzer_assistant').run_tests()
