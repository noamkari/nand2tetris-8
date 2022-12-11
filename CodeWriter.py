"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import os


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.segments_type_dict = {"local": "LCL", "argument": "ARG",
                                   "this": "THIS", "that": "THAT",
                                   "pointer": 3, "temp": 5}
        self._vm_file_name = ''
        self.comp_i = 0
        self.call_i = 0

        self.function_counter = 0
    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self._vm_file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        if command == "add":
            self.output_stream.write(self._binary_operation("+"))

        elif command == "sub":
            self.output_stream.write(self._binary_operation("-"))

        elif command == "neg":
            self.output_stream.write(self._unary_operation("-", "before"))

        elif command == "eq":
            self.output_stream.write(self.compare("JEQ"))

        elif command == "gt":
            self.output_stream.write(self.compare("JGT"))

        elif command == "lt":
            self.output_stream.write(self.compare("JLT"))

        elif command == "and":
            self.output_stream.write(self._binary_operation("&"))

        elif command == "or":
            self.output_stream.write(self._binary_operation("|"))

        elif command == "not":
            self.output_stream.write(self._unary_operation("!", "before"))
        elif command == "shiftleft":
            self.output_stream.write(self._unary_operation("<<", "after"))
        elif command == "shiftright":
            self.output_stream.write(self._unary_operation(">>", "after"))
        # todo >> << shift left and right

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        code = ""
        if command == "C_PUSH":
            if segment == "constant":
                code += f"@{index}\nD=A\n"
            elif segment == "local" or segment == "argument" or segment == "this" or segment == "that":
                code += f"@{index}\nD=A\n@{self.segments_type_dict[segment]}\nA=M+D\nD=M\n"
            elif segment == "pointer" or segment == "temp":
                code += f"@{index}\nD=A\n@{self.segments_type_dict[segment]}\nA=A+D\nD=M\n"
            elif segment == "static":
                code += f"@{self._vm_file_name}.{index}\nD=M\n"
            code += "@SP\nA=M\nM=D\n@SP\nM=M+1\n"

        elif command == "C_POP":
            if segment == "constant":
                code += f"@{index}\nD=A\n"
            elif segment == "local" or segment == "argument" or segment == "this" or segment == "that":
                code += f"@{self.segments_type_dict[segment]}\nD=M\n@{index}\nD=D+A\n"
            elif segment == "pointer" or segment == "temp":
                code += f"@{index}\nD=A\n@{self.segments_type_dict[segment]}\nA=D+A\nD=A\n"
            elif segment == "static":
                code += f"@{self._vm_file_name}.{index}\nD=A\n"

            code += f"@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n"
        self.output_stream.write(code)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        code = f"({label})\n"
        self.output_stream.write(code)

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        code = f"@{label}\n0;JMP\n"
        self.output_stream.write(code)

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        code = f"@SP\nM=M-1\nA=M\nD=M\n@{label}\nD;JNE\n"
        self.output_stream.write(code)

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.write_label(function_name)
        for i in range(n_vars):
            self.write_push_pop("C_PUSH", "constant", 0)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.call_i += 1
        return_address = f"return_{function_name}{self.call_i}"
        self.output_stream.write(f"@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.output_stream.write(f"@{segment}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        # ARG = SP-5-n_args
        self.output_stream.write(f"@{n_args}\nD=A\n@SP\nD=M-D\n@5\nD=D-A\n@ARG\nM=D\n")
        # LCL = SP
        self.output_stream.write(f"@SP\nD=M\n@LCL\nM=D\n")
        self.write_goto(function_name)
        self.write_label(f"return_{function_name}{self.call_i}")

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_stream.write("@LCL\nD=M\n@13\nM=D\n")
        self.output_stream.write("@13\nD=M\n@5\nD=D-A\nA=D\nD=M\n@14\nM=D\n")
        self.output_stream.write(
            "@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n@SP\nM=M-1\n")
        self.output_stream.write("@ARG\nD=M+1\n@SP\nM=D\n")
        for i, segment in enumerate(["THAT", "THIS", "ARG", "LCL"]):
            self.output_stream.write(
                f"@13\nD=M\n@{i + 1}\nA=D-A\nD=M\n@{segment}\nM=D\n")
        self.output_stream.write("@14\nA=M\n0;JMP\n")

    def compare(self, command):
        self.comp_i += 1
        return f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n" \
               f"D=M\n" \
               f"@R13\nM=D\n" \
               f"@YPOS{self.comp_i}\nD;JGT\n" \
               f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n" \
               f"D=M\n" \
               f"@YNEGXPOS{self.comp_i}\nD;JGT\n" \
               f"(CHECK{self.comp_i})\n" \
               f"@R13\nD=D-M\n" \
               f"@TRUE{self.comp_i}\nD;{command}\n" \
               f"@FALSE{self.comp_i}\n0;JMP\n" \
               f"(YPOS{self.comp_i})\n" \
               f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n" \
               f"D=M\n" \
               f"@YPOSXNEG{self.comp_i}\nD;JLT\n" \
               f"@CHECK{self.comp_i}\n0;JMP\n" \
               f"(YNEGXPOS{self.comp_i})\n" \
               f"D=1\n" \
               f"@CHECK{self.comp_i}\n0;JMP\n" \
               f"(YPOSXNEG{self.comp_i})\nD=-1\n" \
               f"@CHECK{self.comp_i}\n0;JMP\n" \
               f"(FALSE{self.comp_i})\n" \
               f"@SP\n" \
               f"A=M\n" \
               f"M=0\n" \
               f"@END{self.comp_i}\n0;JMP\n" \
               f"(TRUE{self.comp_i})\n" \
               f"@SP\n" \
               f"A=M\n" \
               f"M=-1\n" \
               f"@END{self.comp_i}\n0;JMP\n" \
               f"(END{self.comp_i})\n@SP\nM=M+1\n"

    def _unary_operation(self, command, before_after) -> str:
        code = f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n"
        if before_after == "before":
            code += f"M={command}M\n"
        elif before_after == "after":
            code += f"M=M{command}\n"
        return code + f"@SP\n" \
                      f"M=M+1\n"

    # binary

    def _binary_operation(self, command) -> str:
        return f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n" \
               f"D=M\n" \
               f"@SP\n" \
               f"M=M-1\n" \
               f"A=M\n" \
               f"M=M{command}D\n" \
               f"@SP\n" \
               f"M=M+1\n"
