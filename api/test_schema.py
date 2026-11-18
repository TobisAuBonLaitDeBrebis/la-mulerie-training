"""
Tests du contrat OpenAPI (lot 05).

Verifie que le schema drf-spectacular se genere sans avertissement
ni erreur, et documente les points cles du contrat mobile.
"""
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase


class OpenAPISchemaTestCase(TestCase):
    """Le schema OpenAPI doit se generer sans erreur ni warning."""

    def test_schema_generation_fails_on_warn(self):
        fd, path = tempfile.mkstemp(suffix='.yaml')
        os.close(fd)
        try:
            # Equivalent de `manage.py spectacular --fail-on-warn` :
            # leve une SchemaGenerationError en cas d'erreur ou d'avertissement.
            call_command('spectacular', file=path, fail_on_warn=True)

            with open(path, encoding='utf-8') as schema_file:
                schema = schema_file.read()
        finally:
            os.remove(path)

        # Contrats attendus dans le schema
        self.assertIn('/api/v1/dashboard/', schema)
        self.assertIn('/api/v1/horses/', schema)
        self.assertIn('/api/v1/sessions/', schema)
        self.assertIn('/api/v1/me/', schema)
        self.assertIn('client_uuid', schema)
        self.assertIn("description: 'Conflit : UUID client deja utilise avec un contenu different.'", schema)
