# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Definition', fields ['module', 'name']
        db.delete_unique(u'kernel_definition', ['module', 'name'])

        # Deleting model 'Deploy'
        db.delete_table(u'kernel_deploy')

        # Deleting model 'Definition'
        db.delete_table(u'kernel_definition')

        # Adding model 'Repository'
        db.create_table(u'kernel_repository', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=30)),
        ))
        db.send_create_signal(u'kernel', ['Repository'])


    def backwards(self, orm):
        # Adding model 'Deploy'
        db.create_table(u'kernel_deploy', (
            ('text', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'kernel', ['Deploy'])

        # Adding model 'Definition'
        db.create_table(u'kernel_definition', (
            ('category', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('deploy', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['kernel.Deploy'])),
            ('module', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'kernel', ['Definition'])

        # Adding unique constraint on 'Definition', fields ['module', 'name']
        db.create_unique(u'kernel_definition', ['module', 'name'])

        # Deleting model 'Repository'
        db.delete_table(u'kernel_repository')


    models = {
        u'kernel.repository': {
            'Meta': {'object_name': 'Repository'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'kernel.task': {
            'Meta': {'object_name': 'Task'},
            'ack': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'appointment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'archive': ('django.db.models.fields.TextField', [], {}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'check_code': ('django.db.models.fields.SlugField', [], {'default': "'9mRhzt'", 'max_length': '6'}),
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