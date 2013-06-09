# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Task.identifier_code'
        db.alter_column(u'kernel_task', 'identifier_code', self.gf('django.db.models.fields.SlugField')(max_length=6, null=True))

        # Changing field 'Task.token_code'
        db.alter_column(u'kernel_task', 'token_code', self.gf('django.db.models.fields.SlugField')(max_length=6, null=True))
        # Adding unique constraint on 'Task', fields ['token_code', 'identifier_code']
        db.create_unique(u'kernel_task', ['token_code', 'identifier_code'])


    def backwards(self, orm):
        # Removing unique constraint on 'Task', fields ['token_code', 'identifier_code']
        db.delete_unique(u'kernel_task', ['token_code', 'identifier_code'])


        # Changing field 'Task.identifier_code'
        db.alter_column(u'kernel_task', 'identifier_code', self.gf('django.db.models.fields.SlugField')(default='', max_length=6))

        # Changing field 'Task.token_code'
        db.alter_column(u'kernel_task', 'token_code', self.gf('django.db.models.fields.SlugField')(default='', max_length=6))

    models = {
        u'kernel.task': {
            'Meta': {'unique_together': "(('identifier_code', 'token_code'),)", 'object_name': 'Task'},
            'ack': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'appointment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'archive': ('django.db.models.fields.TextField', [], {}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'check_code': ('django.db.models.fields.SlugField', [], {'default': "'yn4Klg'", 'max_length': '6'}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'ex_data': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier_code': ('django.db.models.fields.SlugField', [], {'max_length': '6', 'null': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_tasks'", 'null': 'True', 'to': u"orm['kernel.Task']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '16'}),
            'token_code': ('django.db.models.fields.SlugField', [], {'max_length': '6', 'null': 'True'}),
            'ttl': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['kernel']