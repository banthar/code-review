#!/usr/bin/python
# -*- coding: utf-8 -*-

title = 'Code Review'

favicon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAQAAADZc7J/AAABoUlEQVRIx93UsW7TUBTG8V9TKEuDkDqgZskdmJCYLBZUqd6YWJqtEgpbH4AHKDwAMwNC6cSEGDp26QOQDoRORSgOoCxkALUDDYMZYqWhsd3WbBxv/s7567vnnnsWzEcQkEhcOWIdfWn29XXEly8OtmeKzyDbQlnZwkz5EwwdODBEQyTSwI7nFx0n6EilutqaVtTVrWhq60qlOuUuaOtL7Vq3/Nf/Zet2pfra5a3bl+rasDSnLdnQldovauc1NAVDb+wZz+lje4JVQTMfUMvuPXHoJDfjxKEkm41cwEQalPQ5MZiOV66DidVxIaBMmwIqRy2b+VWrhTkTreBt1DIplIzKpMlJ8REGEkFLlJsRaQlZI0sn8dgLjTml4ZVfvnt6mbcwsnPOReSt31Kp99bySxfBDx/c8sAd9wR1NzVENm2J3cic3PfRl4v3wamRxJEjiZFTX32a7oZekYvyjbSmdxXExEssnrnWWUTX3SrjNot453Y1xFkvXldDPPLzXxGPHf9/iJfntngFRGuxAqDnm4eug89VN9lW5iCuvgxjz8T8AZ5a'vzw+wvefAAAAAElFTkSuQmCC"

style = """
* {
  padding: 0;
  margin: 0;
  list-style-type: none;
}

nav {
  background-color: #333;
  overflow: hidden;
}

nav ul li {
  display: inline-block;
	padding: 0.5em 0.75em;
}

nav > ul > li > a {
  color: #aaa;
  text-decoration: none;
	font-size: 15px;
	font-family: sans-serif;
}

nav li:hover {
  background-color: #666;
}

body {
  background-color: #eee;
}

body > div {
  background-color: #fff;
	padding: 1.0em;
	margin: 1.0em;
	font-family: monospace;
	box-shadow: 2px 2px 10px #888888;
}

table {
	border-collapse: collapse;
	width: 100%;
}

td {
  padding: 0.25em;
}

tr:nth-child(even) {
	background: #f8f8f8;
}

tr:nth-child(odd) {
	background: #eeeeee;
}

tr:hover {
	background: #ddd;
}

input {
	margin: 0.25em;
	padding: 0.25em;
	border: 1px solid;
	border-radius: 2px;
}

hr {
  margin: 0.25em;
	border: none;
  border-top: 1px solid black;
}

.diff div {
	margin: 0px;
	padding: 0px;
  white-space: pre;
}

.diff .added {
	background-color: #cfd;
}

.diff .removed {
	background-color: #fdc;
}

.diff .header {
	font-weight: bold;
}

"""
