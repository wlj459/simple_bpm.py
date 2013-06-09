# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Record'
        db.create_table(u'log_record', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('logger', self.gf('django.db.models.fields.SlugField')(max_length=32)),
            ('revision', self.gf('django.db.models.fields.SlugField')(max_length=12)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('module', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('lineno', self.gf('django.db.models.fields.IntegerField')()),
            ('message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'log', ['Record'])


    def backwards(self, orm):
        # Deleting model 'Record'
        db.delete_table(u'log_record')


    models = {
        u'log.record': {
            'Meta': {'object_name': 'Record'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'lineno': ('django.db.models.fields.IntegerField', [], {}),
            'logger': ('django.db.models.fields.SlugField', [], {'max_length': '32'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'module': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'revision': ('django.db.models.fields.SlugField', [], {'max_length': '12'})
        }
    }

    complete_apps = ['log']