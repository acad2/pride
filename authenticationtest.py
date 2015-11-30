import pride.authentication
Authentication_Table = pride.authentication.Authentication_Table

def test_authentication_table():
    table = Authentication_Table()
    bytestream = table.save()
    table_again = Authentication_Table.load(bytestream)
    code_sequence = table_again.generate_challenge()
    assert table.rows == table_again.rows
    assert table.get_passcode(*code_sequence) == table_again.get_passcode(*code_sequence)   