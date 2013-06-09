# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Definition'
        db.create_table(u'kernel_definition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('category', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'kernel', ['Definition'])

        # Adding model 'Task'
        db.create_table(u'kernel_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sub_tasks', null=True, to=orm['kernel.Task'])),
            ('args', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('ex_data', self.gf('django.db.models.fields.TextField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default='PENDING', max_length=16)),
            ('appointment', self.gf('django.db.models.fields.CharField')(default='', max_length=16, blank=True)),
            ('identifier_code', self.gf('django.db.models.fields.SlugField')(max_length=6)),
            ('token_code', self.gf('django.db.models.fields.SlugField')(max_length=6)),
            ('archive', self.gf('django.db.models.fields.TextField')()),
            ('ack', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('check_code', self.gf('django.db.models.fields.SlugField')(default='Id3s6P', max_length=6)),
            ('ttl', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'kernel', ['Task'])


    def backwards(self, orm):
        # Deleting model 'Definition'
        db.delete_table(u'kernel_definition')

        # Deleting model 'Task'
        db.delete_table(u'kernel_task')


    models = {
        u'kernel.definition': {
            'Meta': {'object_name': 'Definition'},
            'category': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'kernel.task': {
            'Meta': {'object_name': 'Task'},
            'ack': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'appointment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'archive': ('django.db.models.fields.TextField', [], {}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'check_code': ('django.db.models.fields.SlugField', [], {'default': "'Id3s6P'", 'max_length': '6'}),
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