#! /usr/local/bin/ruby
$:.unshift File.dirname(__FILE__) + '/sinatra/lib'
require 'sinatra'

require 'rubygems'
require 'sinatra'

get '/' do
  haml :index
end