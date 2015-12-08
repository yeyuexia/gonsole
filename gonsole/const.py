# coding: utf8

STANDARD_SPACE = "    "
PRINTLN = "fmt.Println({})"
GO_TEMPLATE = """package main

import (
{%import_area%}
)

{%func_area%}

func main() {
{%code_area%}
}
"""
