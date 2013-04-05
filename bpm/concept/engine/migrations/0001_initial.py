# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Defination'
        db.create_table(u'engine_defination', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('category', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'engine', ['Defination'])

        # Adding model 'Process'
        db.create_table(u'engine_process', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('is_subprocess', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pickled', self.gf('django.db.models.fields.TextField')(db_column='pickle')),
        ))
        db.send_create_signal(u'engine', ['Process'])

        # Adding model 'Task'
        db.create_table(u'engine_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('args', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.TextField')()),
            ('is_complete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('result', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'engine', ['Task'])


    def backwards(self, orm):
        # Deleting model 'Defination'
        db.delete_table(u'engine_defination')

        # Deleting model 'Process'
        db.delete_table(u'engine_process')

        # Deleting model 'Task'
        db.delete_table(u'engine_task')


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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_subprocess': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pickled': ('django.db.models.fields.TextField', [], {'db_column': "'pickle'"}),
            'state': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'engine.task': {
            'Meta': {'object_name': 'Task'},
            'args': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'result': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['engine']