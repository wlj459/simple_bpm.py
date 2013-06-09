# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Definition.module'
        db.add_column(u'kernel_definition', 'module',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Definition.module'
        db.delete_column(u'kernel_definition', 'module')


    models = {
        u'kernel.definition': {
            'Meta': {'object_name': 'Definition'},
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'kernel.task': {
            'Meta': {'object_name': 'Task'},
            'ack': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'appointment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'archive': ('django.db.models.fields.TextField', [], {}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'check_code': ('django.db.models.fields.SlugField', [], {'default': "'d0hsEa'", 'max_length': '6'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'ex_data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier_code': ('django.db.models.fields.SlugField', [], {'max_length': '6'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_tasks'", 'null': 'True', 'to': u"orm['kernel.Task']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '16'}),
            'token_code': ('django.db.models.fields.SlugField', [], {'max_length': '6'}),
            'ttl': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['kernel']