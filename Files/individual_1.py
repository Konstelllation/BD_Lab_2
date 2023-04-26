#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Для своего варианта лабораторной работы 2.17 необходимо реализовать хранение данных в
базе данных SQLite3.
"""

import sqlite3
import typing as t
from pathlib import Path
import argparse


def adding(
        database_path: Path,
        name: str,
        group: int,
        progress: str
) -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Получить идентификатор студента в базе данных.
    # Если такой записи нет, то добавить информацию о студенте
    cursor.execute(
        """
        SELECT student_id FROM student_name WHERE name = ?
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO student_name (name) VALUES (?)
            """,
            (name,)
        )
        student_id = cursor.lastrowid
    else:
        student_id = row[0]

        # Добавить информацию о новом студенте.
    cursor.execute(
        """
        INSERT INTO students (student_id, name, groupp, progress)
        VALUES (?, ?, ?, ?)
        """,
        (student_id, name, group, progress)
    )
    conn.commit()
    conn.close()


def all_students(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """Выбрать всех студентов"""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT student_name.name, students.groupp, students.progress
        FROM students
        INNER JOIN student_name ON student_name.student_id = students.student_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "group": row[1],
            "progress": row[2],

        }
        for row in rows
    ]


def select_student(database_path: Path, progress: str) -> t.List[t.Dict[str, t.Any]]:
    """Выбрать студента"""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT students.name, students.groupp, students.progress
        FROM students
        INNER JOIN student_name ON student_name.student_id = students.student_id
        WHERE students.progress == ?
        """,
        (progress,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "name": row[0],
            "group": row[1],
            "progress": row[2],
        }
        for row in rows
    ]


def display(students: t.List[t.Dict[str, t.Any]]) -> None:
    if students:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^20} |'.format(
                "No",
                "ФИО",
                "Группа",
                "Успеваемость"
            )
        )
        print(line)
        for idx, student in enumerate(students, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>20} |'.format(
                    idx,
                    student.get('name', ''),
                    student.get('group', ''),
                    student.get('progress', 0)
                )
            )
            print(line)


def create_data(database_path: Path) -> None:
    """Создать базу данных"""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    # Создать таблицу с ФИО студентов
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_name (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        )
        """
    )
    # Создать таблицу с полной информацией о студентах
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        groupp INTEGER NOT NULL,
        progress TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES student_name(student_id)
        )
        """
    )
    conn.close()


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "students.db"),
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("students")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления студентов.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new student"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The students's name"
    )
    add.add_argument(
        "-g",
        "--group",
        action="store",
        type=int,
        help="The student's group"
    )
    add.add_argument(
        "-p",
        "--progress",
        action="store",
        required=True,
        help="The student's progress"
    )
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all students"
    )
    # Создать субпарсер для выбора студентов.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the students"
    )
    select.add_argument(
        "-s",
        "--select",
        action="store",
        required=True,
        help="The students's name"
    )
    args = parser.parse_args(command_line)
    db_path = Path(args.db)
    create_data(db_path)
    if args.command == "add":
        adding(db_path, args.name, args.group, args.progress)
    elif args.command == "select":
        display(select_student(db_path, args.select))
    elif args.command == "display":
        display(all_students(db_path))
    pass


if __name__ == '__main__':
    main()
