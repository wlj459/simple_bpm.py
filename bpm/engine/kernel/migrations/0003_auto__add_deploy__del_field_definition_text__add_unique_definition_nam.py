# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Deploy'
        db.create_table(u'kernel_deploy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'kernel', ['Deploy'])

        # Deleting field 'Definition.text'
        db.delete_column(u'kernel_definition', 'text')

        # Adding unique constraint on 'Definition', fields ['name', 'module']
        db.create_unique(u'kernel_definition', ['name', 'module'])


    def backwards(self, orm):
        # Removing unique constraint on 'Definition', fields ['name', 'module']
        db.delete_unique(u'kernel_definition', ['name', 'module'])

        # Deleting model 'Deploy'
        db.delete_table(u'kernel_deploy')

        # Adding field 'Definition.text'
        db.add_column(u'kernel_definition', 'text',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    models = {
        u'kernel.definition': {
            'Meta': {'unique_together': "(('module', 'name'),)", 'object_name': 'Definition'},
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100'})
        },
        u'kernel.deploy': {
            'Meta': {'object_name': 'Deploy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'kernel.task': {
            'Meta': {'object_name': 'Task'},
            'ack': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'appointment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'archive': ('django.db.models.fields.TextField', [], {}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'check_code': ('django.db.models.fields.SlugField', [], {'default': "'TTE74F'", 'max_length': '6'}),
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