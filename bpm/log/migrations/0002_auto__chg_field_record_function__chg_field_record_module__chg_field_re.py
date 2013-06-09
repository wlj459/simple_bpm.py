# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Record.function'
        db.alter_column(u'log_record', 'function', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Record.module'
        db.alter_column(u'log_record', 'module', self.gf('django.db.models.fields.CharField')(max_length=256))

        # Changing field 'Record.revision'
        db.alter_column(u'log_record', 'revision', self.gf('django.db.models.fields.SlugField')(max_length=32))

    def backwards(self, orm):

        # Changing field 'Record.function'
        db.alter_column(u'log_record', 'function', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'Record.module'
        db.alter_column(u'log_record', 'module', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'Record.revision'
        db.alter_column(u'log_record', 'revision', self.gf('django.db.models.fields.SlugField')(max_length=12))

    models = {
        u'log.record': {
            'Meta': {'object_name': 'Record'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'lineno': ('django.db.models.fields.IntegerField', [], {}),
            'logger': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'revision': ('django.db.models.fields.SlugField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['log']