# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Task.is_confirmed'
        db.add_column(u'engine_task', 'is_confirmed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Process.is_locked'
        db.add_column(u'engine_process', 'is_locked',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Task.is_confirmed'
        db.delete_column(u'engine_task', 'is_confirmed')

        # Deleting field 'Process.is_locked'
        db.delete_column(u'engine_process', 'is_locked')


    models = {
        u'engine.defination': {
            'Meta': {'object_name': 'Defination'},
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '255'})
        },
        u'engine.process': {
            'Meta': {'object_name': 'Process'},
            'defination': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['engine.Defination']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_subprocess': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pickled': ('django.db.models.fields.TextField', [], {'db_column': "'pickle'"}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'engine.task': {
            'Meta': {'object_name': 'Task'},
            'args': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'process': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['engine.Process']"}),
            'result': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['engine']