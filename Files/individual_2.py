#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Самостоятельно изучите работу с пакетом python-psycopg2 для работы с базами
данных PostgreSQL. Для своего варианта лабораторной работы 2.17 необходимо
реализовать возможность хранения данных в базе данных СУБД PostgreSQL.
"""

import argparse
import psycopg2
import typing as t
from pathlib import Path


def connect():
    conn = psycopg2.connect(
        user="postgres",
        password="12345",
        host="localhost",
        port="5432")

    return conn


def adding(
        name: str,
        groupp: int,
        progress: str
) -> None:
    """Добавить студента в базу данных"""
    # Получить идентификатор студента в базе данных.
    # Если такой записи нет, то добавить информацию о новом студенте.
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT student_id FROM students WHERE name = %s;
        """,
        (name,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO student (name) VALUES (%s)
            """,
            (name,)
        )
        student_id = cursor.lastrowid
    else:
        student_id = row[0]

        # Добавить информацию о новом студенте.
    cursor.execute(
        """
        INSERT INTO students (student_id, progress, groupp)
        VALUES (%s, %s, %s)
        """,
        (student_id, progress, groupp)
    )
    connect().commit()


def all_students(progress) -> t.List[t.Dict[str, t.Any]]:
    """Выбрать всех студентов"""
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT student.name, students.groupp, students.progress
        FROM students
        INNER JOIN student ON student_name.student_id = students.student_id
        WHERE studens.progress = %s
        """,
        (progress,)
    )
    rows = cursor.fetchall()
    return [
        {
            "name": row[0],
            "groupp": row[1],
            "progress": row[2],
        }
        for row in rows
    ]


def select_student():
    """Выбрать студента"""
    cursor = connect().cursor()
    cursor.execute(
        """
        SELECT student.name, students.groupp, students.progress
        FROM students
        INNER JOIN student ON student.student_id = students.student_id
        """
    )
    rows = cursor.fetchall()
    return [
        {
            "name": row[0],
            "groupp": row[1],
            "progress": row[2],
        }
        for row in rows
    ]


def display(students: t.List[t.Dict[str, t.Any]]) -> None:
    """Отобразить список студентво"""
    if students:
        line = '+-{}-+-{}-+-{}-+'.format(
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
                '| {:>4} | {:<30} | {:<20} | {:<20} |'.format(
                    idx,
                    student.get('name', ''),
                    student.get('groupp', ''),
                    student.get('progress', 0)

                )
            )
            print(line)
        else:
            print("Список пуст")


def create_data() -> None:
    """Создать базу данных"""
    # Создать таблицу с информацией о направлениях маршрутов.
    cursor = connect().cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student (
        student_id serial,
        PRIMARY KEY(student_id),
        name TEXT NOT NULL
        )
        """
    )
    # Создать таблицу с информацией о студентах
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
        student_id serial,
        PRIMARY KEY(student_id),
        groupp INTEGER NOT NULL,
        progress TEXT NOT NULL,
        FOREIGN KEY(student_id) REFERENCES student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
        )
        """
    )


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "students.db"),
        help="The database file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("students")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления студента.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new student"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        help="The student's name"
    )
    add.add_argument(
        "-g",
        "--group",
        action="store",
        required=True,
        help="The student's group"
    )
    add.add_argument(
        "-p",
        "--progress",
        action="store",
        required=True,
        help="The student's prograss"
    )
    # Создать субпарсер для отображения всех студентов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all students"
    )
    # Создать субпарсер для выбора студента.
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
        help="The required progress"
    )
    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)
    create_data()
    # Добавить студента.
    if args.command == "add":
        adding(args.name, args.group, args.progress)
    elif args.command == "select":
        display(all_students(args.progress))
    elif args.command == "display":
        display(select_student())
    pass


if __name__ == '__main__':
    main()
